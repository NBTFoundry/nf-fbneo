# SPDX-License-Identifier: MPL-2.0
"""FinalBurn Neo on the libretro host, under Xvfb, with a romset made here (no
game or BIOS is shipped): the Space Invaders board's four ROMs hold a small
8080 program of ours, each file padded and given the CRC-32 the driver
expects, so the core takes the set as its own. The game list (titles, BIOS
sets left out), the zipped set running turned upright, save states and
--game; and the signed package's declaration."""

import os
from pathlib import Path
import re
import select
import shutil
import signal
import socket
import struct
import subprocess
import tempfile
import time
import unittest
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
APP = Path(os.environ.get("NBT_FBNEO_APP", ROOT / "build/nbt-fbneo-host"))
MGR_DIR = Path(os.environ.get("NBT_MGR_DIR", ROOT.parent / "manager"))
DRIVER = ROOT / "third_party/fbneo/src/burn/drv/pre90s/d_invaders.cpp"

SOUTH, VIEW, MENU, DOWN = 1 << 0, 1 << 6, 1 << 7, 1 << 12
XBOX = 1

# What the program writes to RAM: the complement of these bytes, so they are
# nowhere in the program itself.
MARKER = b"NBT FBNEO RUNS"


def invaders_roms():
    """The ROMs of upstream's invaders driver (name, size, CRC-32), read from
    its source: the one list of them."""
    text = DRIVER.read_text(encoding="latin-1")
    desc = re.search(r"invadersRomDesc\[\] = \{(.*?)\n\};", text, re.S).group(1)
    return [(name, int(size, 16), int(crc, 16)) for name, size, crc in
            re.findall(r'\{ "([^"]+)",\s*(0x[0-9a-fA-F]+),\s*(0x[0-9a-fA-F]+),', desc)]


def i8080_program() -> bytes:
    """8080 code at 0x0000: the stack set, the complement of MARKER written
    to the work RAM at 0x2000, then a loop."""
    code = bytearray([0x31, 0x00, 0x24])  # lxi sp, 2400h
    code += bytes([0x21, 0x00, 0x20])  # lxi h, 2000h
    for byte in MARKER:
        code += bytes([0x36, byte ^ 0xFF, 0x23])  # mvi m, ~byte ; inx h
    here = len(code)
    code += bytes([0xC3, here & 0xFF, here >> 8])  # jmp $
    return bytes(code)


def crc_entry(i: int) -> int:
    """Entry i of the CRC-32 table (reflected polynomial 0xEDB88320)."""
    for _ in range(8):
        i = (i >> 1) ^ 0xEDB88320 if i & 1 else i >> 1
    return i


# The table's entries have distinct top bytes: the top byte names the index.
CRC_INDEX = {crc_entry(i) >> 24: i for i in range(256)}


def forge(data: bytes, size: int, crc: int) -> bytes:
    """`data` padded to `size` bytes, its last four chosen so that the whole
    has CRC-32 `crc`: the register run back from the wanted value over four
    bytes gives what they must be."""
    assert len(data) <= size - 4
    body = data + bytes(size - 4 - len(data))
    reg = crc ^ 0xFFFFFFFF
    for _ in range(4):
        i = CRC_INDEX[reg >> 24]
        reg = ((reg ^ crc_entry(i)) << 8 & 0xFFFFFFFF) | i
    tail = (reg ^ zlib.crc32(body) ^ 0xFFFFFFFF).to_bytes(4, "little")
    out = body + tail
    assert zlib.crc32(out) == crc, hex(zlib.crc32(out))
    return out


def romset_zip() -> bytes:
    """invaders.zip: the program in the first ROM, the others empty, each
    with the driver's CRC-32."""
    out = Path(tempfile.mkstemp(suffix=".zip")[1])
    try:
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n, (name, size, crc) in enumerate(invaders_roms()):
                z.writestr(name, forge(i8080_program() if n == 0 else b"", size, crc))
        return out.read_bytes()
    finally:
        out.unlink()


def complement(data: bytes) -> bytes:
    return bytes(b ^ 0xFF for b in data)


def xvfb():
    r, w = os.pipe()
    proc = subprocess.Popen(
        ["Xvfb", "-displayfd", str(w), "-screen", "0", "1280x480x24", "-nolisten", "tcp"],
        pass_fds=(w,), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.close(w)
    number = b""
    while not number.endswith(b"\n"):
        ready, _, _ = select.select([r], [], [], 10)
        chunk = os.read(r, 1) if ready else b""
        if not chunk:
            break
        number += chunk
    os.close(r)
    return proc, ":" + number.decode().strip()


class App:
    """The emulator, its log (standard error) read by line."""

    def __init__(self, env, pass_fds, args=()):
        full = {k: v for k, v in os.environ.items() if not k.startswith("NBT_")}
        full.update(env)
        self.proc = subprocess.Popen([str(APP), *args], stdout=subprocess.DEVNULL,
                                     stderr=subprocess.PIPE, env=full, pass_fds=pass_fds)
        self.lines, self.buf = [], b""

    def wait(self, pattern, timeout=60.0):
        regex, deadline = re.compile(pattern), time.monotonic() + timeout
        while True:
            while b"\n" in self.buf:
                raw, self.buf = self.buf.split(b"\n", 1)
                self.lines.append(raw.decode(errors="replace"))
            for i, line in enumerate(self.lines):
                if regex.search(line):
                    del self.lines[: i + 1]
                    return line
            fd = self.proc.stderr.fileno()
            left = deadline - time.monotonic()
            ready, _, _ = select.select([fd], [], [], max(0.0, left)) if left > 0 else ([], [], [])
            chunk = os.read(fd, 4096) if ready else b""
            if not chunk:
                raise AssertionError(f"no line matching {pattern!r}; saw {self.lines[-20:]!r}")
            self.buf += chunk

    def stop(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGTERM)
        _, err = self.proc.communicate(timeout=60)
        self.buf += err
        return self.proc.returncode


class RomsetTest(unittest.TestCase):
    def test_the_romset_has_the_drivers_crcs(self):
        roms = invaders_roms()
        self.assertEqual(len(roms), 4)
        with zipfile.ZipFile(__import__("io").BytesIO(romset_zip())) as z:
            for name, size, crc in roms:
                info = z.getinfo(name)
                self.assertEqual((info.file_size, info.CRC), (size, crc))


@unittest.skipUnless(os.access(APP, os.X_OK), f"{APP} not built")
@unittest.skipUnless(shutil.which("Xvfb"), "Xvfb not installed")
class PlayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="nbt-fbneo-"))
        self.files, self.data = self.tmp / "files", self.tmp / "data"
        self.files.mkdir(mode=0o700)
        self.data.mkdir(mode=0o700)
        (self.files / "invaders.zip").write_bytes(romset_zip())
        self.x, self.display = xvfb()
        self.pad_app, self.pad = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.seq = 0

    def tearDown(self):
        self.pad_app.close()
        self.pad.close()
        self.x.terminate()
        self.x.wait(timeout=5)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def start(self, *args, **settings):
        env = {
            "NBT_LAUNCH": "user", "DISPLAY": self.display, "LIBGL_ALWAYS_SOFTWARE": "1",
            "NBT_NO_AUDIO": "1", "NBT_FILES_DIR": str(self.files), "NBT_DATA_DIR": str(self.data),
            "NBT_BRIDGE_CAPS": "gamepad", "NBT_GAMEPAD_FD": str(self.pad_app.fileno()),
        }
        env.update({"NBT_SETTING_" + k.upper(): v for k, v in settings.items()})
        app = App(env, (self.pad_app.fileno(),), args)
        self.addCleanup(lambda: app.proc.poll() is None and app.proc.kill())
        app.wait(r"core FinalBurn Neo ")
        return app

    def press(self, buttons=0, hold=0.15):
        self.seq += 1
        self.pad.send(struct.pack("<BBBBIIhhhhHH", 1, 1, 1, XBOX, self.seq, buttons, 0, 0, 0, 0, 0, 0))
        time.sleep(hold)

    def tap(self, buttons):
        self.press(buttons)
        self.press(0)

    def menu(self, downs):
        """The pause menu (View + Menu), `downs` items down, chosen."""
        self.tap(VIEW | MENU)
        for _ in range(downs):
            self.tap(DOWN)
        self.tap(SOUTH)

    def play(self, seconds):
        """Lets the game run, the pad idle but plugged in."""
        for _ in range(int(seconds / 0.15)):
            self.press(0)

    def test_a_romset_is_listed_by_title_and_runs_and_a_state_is_saved(self):
        # A BIOS set (left out of the list), a file the core does not know
        # (listed by its name, after the titles): the first entry is the game.
        (self.files / "neogeo.zip").write_bytes(romset_zip())
        (self.files / "zzz-unknown.zip").write_bytes(b"PK\5\6" + bytes(18))
        app = self.start()
        self.press(0)
        self.tap(SOUTH)
        app.wait(r"Romset description: Space Invaders")
        app.wait(r"game invaders\.zip: \d+x\d+, (59|60)\.\d+ fps")
        self.play(1.5)
        self.menu(1)  # Save state
        app.wait(r"State saved in slot 1")
        state = (self.data / "states" / "invaders.zip.state1").read_bytes()
        self.assertIn(complement(MARKER), state)  # the program ran
        self.menu(2)  # Load state
        app.wait(r"State of slot 1 loaded")
        self.assertEqual(app.stop(), 0)
        self.assertEqual((self.data / "last-game").read_bytes(), b"invaders.zip")

    def test_a_vertical_game_is_turned_and_takes_its_aspect(self):
        # Space Invaders' monitor stands on its side: its 3:4 picture is the
        # frame turned a quarter.
        app = self.start("--game", "invaders.zip")
        app.wait(r"game invaders\.zip: \d+x\d+, .*, aspect 0\.750, 1 quarter turns$")
        self.play(0.5)
        self.assertEqual(app.stop(), 0)


class PackageTest(unittest.TestCase):
    def test_the_package_declares_files_and_its_settings(self):
        verify = MGR_DIR / "build" / "nbt-verify"
        if not (MGR_DIR / "tools/package.py").exists() or not verify.exists():
            self.skipTest("the manager's tools/package.py or build/nbt-verify is missing")
        if not shutil.which("openssl"):
            self.skipTest("openssl is missing")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            key, public = tmp / "app.key", tmp / "app.pub"
            subprocess.run(["openssl", "genrsa", "-out", key, "3072"], check=True, capture_output=True)
            subprocess.run(["openssl", "rsa", "-in", key, "-pubout", "-out", public], check=True,
                           capture_output=True)
            # A stand-in for the guest: ARM ET_EXEC with the SDK's NBT ABI note.
            binary = tmp / "stand-in.guest"
            note = struct.pack("<III", 4, 12, 1) + b"NBT\0" + struct.pack("<III", 1, 1, 2)
            elf = bytearray(52)
            elf[:7] = b"\x7fELF\x01\x01\x01"
            struct.pack_into("<HHI", elf, 16, 2, 40, 1)
            struct.pack_into("<I", elf, 28, 52)
            struct.pack_into("<HHH", elf, 40, 52, 32, 1)
            phdr = struct.pack("<IIIIIIII", 4, 84, 0, 0, len(note), len(note), 4, 4)
            binary.write_bytes(bytes(elf) + phdr + note)
            subprocess.run(["make", "-s", "-C", str(ROOT), "package", f"BUILD_DIR={tmp}",
                            f"PACKAGE_INPUT={binary}", f"APP_KEY={key}", f"NBT_MGR_DIR={MGR_DIR}",
                            "APP_VERSION=0.0.1"], check=True, capture_output=True)
            package = tmp / "fbneo-0.0.1.nbt"
            out = subprocess.run([str(verify), str(package), str(public), "fbneo", "nbt_6.5_armv7"],
                                 check=True, capture_output=True, text=True).stdout
            self.assertIn("app=fbneo\n", out)
            self.assertIn("bridge=1.7\n", out)
            self.assertIn("bridge-uses=show,controller,files,runner\n", out)
            self.assertIn("bridge-optional=status,live-settings,gamepad\n", out)
            raw = package.read_bytes()
            manifest = raw[24 : 24 + int.from_bytes(raw[8:12], "big")].decode("ascii")
            self.assertIn("bridge-files=zip,7z|512|16384\n", manifest)
            for setting in ("neogeo|Neo Geo|auto|auto,mvs,aes,unibios",
                            "frameskip|Frame skip|off|off,auto,1,2"):
                self.assertIn(f"setting={setting}\n", manifest)


if __name__ == "__main__":
    unittest.main()
