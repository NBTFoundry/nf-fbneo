#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Writes legal/NOTICE.txt: the notices the application's guest carries.

Ours (MPL-2.0); FinalBurn Neo's licence and the MAME licence it is subject
to; the code in it under other licences (the LGPL sound chips, the per-file
BSD-3-Clause and MIT sources with their copyright holders); the libraries
it bundles and the guest links (read from their own files); the NBT App SDK
(MPL-2.0) and its third-party notices (NBT_SDK_DIR, default ../sdk); and
picolibc, which the NBT toolchain's runtime links statically (NBT_TOOLCHAIN,
default the SDK's installed release). Run again when the pin, a bundled
library or the toolchain changes.
"""
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get("NBT_SDK_DIR", ROOT.parent / "sdk"))
CORE = ROOT / "third_party/fbneo"
SRC = CORE / "src"
LIBS = SRC / "dep/libs"
LIBRETRO = SRC / "burner/libretro"
RULE = "\n" + "=" * 72 + "\n\n"

HEADER = """NBTFoundry

NBTFoundry nf-fbneo
Copyright (c) 2026 Fabien Poussin
Original software: MPL-2.0. You may redistribute and modify it under that license.
This software comes WITHOUT ANY WARRANTY, to the extent permitted by law.
Original NBTFoundry artwork: MPL-2.0. Trademark rights are separate.
Source: https://github.com/NBTFoundry/nf-fbneo
When redistributing binaries, include applicable notices and provide the source required by the component licenses.

The application's binary contains FinalBurn Neo, whose licence permits no
monetary gain of any kind (no sale, lease or rent, no donations): the
binary, as a whole, may be distributed only on FinalBurn Neo's terms below,
which also bind it to the MAME licence. Its source is the repository above
with its submodule (libretro/FBNeo) and the NBT App SDK it names
(release/sdk.ref). No ROM image, game or BIOS is included.
"""


def toolchain() -> Path:
    if os.environ.get("NBT_TOOLCHAIN"):
        return Path(os.environ["NBT_TOOLCHAIN"])
    version = re.search(r"^NBT_TOOLCHAIN_VERSION := (\S+)", (SDK / "module/flags.mk").read_text(), re.M)
    return SDK / "toolchain" / f"nbt-toolchain-{version.group(1)}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def leading_comment(path: Path) -> str:
    """A source file's licence: its first block comment, without the comment marks."""
    text = read(path)
    block = text[text.index("/*") + 2 : text.index("*/")]
    return "\n".join(re.sub(r"^ ?\* ?", "", line).rstrip() for line in block.strip("\n").split("\n")) + "\n"


def line_comments(path: Path, count: int) -> str:
    """The first `count` lines of a file whose licence is in // comments."""
    lines = read(path).split("\n")[:count]
    return "\n".join(re.sub(r"^/[/*] ?|\*/$", "", line).rstrip() for line in lines) + "\n"


def tagged(licence: str):
    """FinalBurn Neo's sources tagged with `licence` (MAME's "// license:" lines)
    and their copyright holders."""
    files, holders = [], set()
    for path in sorted(SRC.rglob("*")):
        if path.suffix not in (".c", ".cpp", ".h") or "dep/libs" in str(path) or "intf/video" in str(path):
            continue
        head = read(path)[:600]
        tag = re.search(r"license:\s*([^\s*]+)", head, re.I)
        if not tag or tag.group(1).lower() != licence.lower():
            continue
        files.append(str(path.relative_to(SRC)))
        found = re.search(r"copyright-holders:\s*(.+)", head, re.I)
        if found:
            holders.update(h.strip() for h in found.group(1).strip(" */").split(","))
    return files, sorted(h for h in holders if h)


def stb_vorbis_licence() -> str:
    text = read(LIBS / "stb_vorbis/stb_vorbis.c")
    start = text.rindex("This software is available under 2 licenses")
    return text[start : text.index("*/", start)].rstrip() + "\n"


def r8brain_licence() -> str:
    text = leading_comment(LIBS / "r8brain/r8bbase.h")
    return text[text.index("The MIT License") :]


def main():
    runtime = toolchain() / "share/licenses/picolibc"
    if not runtime.is_dir():
        sys.exit(f"no picolibc notices in {runtime}: set NBT_TOOLCHAIN")
    revision = subprocess.run(["git", "-C", str(CORE), "rev-parse", "--short=12", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
    sdk_notices = subprocess.run([sys.executable, str(SDK / "tools/third_party_notices.py")],
                                 check=True, capture_output=True, text=True).stdout
    bsd_files, bsd_holders = tagged("BSD-3-Clause")
    mit_files, _ = tagged("MIT")
    lics = ROOT / "LICENSES"
    parts = [
        HEADER,
        "Head-unit risk and disclaimer\n\n" + read(ROOT / "DISCLAIMER.md").split("\n", 1)[1],
        "MPL-2.0: this application and the NBT App SDK (https://github.com/NBTFoundry/sdk)\n\n"
        + read(lics / "MPL-2.0.txt"),
        f"FinalBurn Neo, the emulator (third_party/fbneo, libretro/FBNeo at {revision})\n"
        "https://github.com/finalburnneo/FBNeo; its licence, verbatim (src/license.txt):\n\n"
        + read(SRC / "license.txt"),
        "The MAME License, which FinalBurn Neo is subject to (above), from\n"
        "https://raw.githubusercontent.com/mamedev/mame/5cef4e1f91010f0d573bbd662208979fa39e73ec/docs/mamelicense.txt\n\n"
        + read(lics / "LicenseRef-MAME.txt"),
        "FinalBurn Neo's sources under the BSD-3-Clause licence (\"license:BSD-3-Clause\" in their\n"
        f"headers: {len(bsd_files)} files). Copyright holders: " + ", ".join(bsd_holders) + ".\n\n"
        + read(lics / "BSD-3-Clause.txt"),
        "FinalBurn Neo's sources under the MIT licence: " + ", ".join(mit_files) + "\n\n"
        + read(lics / "MIT.txt"),
        "HuC6280 PSG (src/burn/snd/c6280.cpp), under the GNU LGPL 2.1 or later\n\n"
        + leading_comment(SRC / "burn/snd/c6280.cpp"),
        "YMF278B (src/burn/snd/ymf278b.c), under the MAME license or the GNU LGPL 2.1\n\n"
        + leading_comment(SRC / "burn/snd/ymf278b.c"),
        "The GNU Lesser General Public License 2.1 (above)\n\n" + read(lics / "LGPL-2.1-or-later.txt"),
        "Z180 and uPD7810 CPU cores (src/cpu/z180, src/cpu/upd7810), dual-licensed under the MAME\n"
        "license or the GNU GPL 2 or later (the text in LICENSES/GPL-2.0-or-later.txt)\n\n"
        + leading_comment(SRC / "cpu/z180/z180.cpp"),
        "zlib 1.3.1 (src/dep/libs/zlib)\n\n" + leading_comment(LIBS / "zlib/zlib.h"),
        "Minizip, the zip reader (src/burner/unzip.c, ioapi.c), under the zlib licence\n\n"
        + leading_comment(SRC / "burner/unzip.c"),
        "LZMA SDK, the 7z reader and LZMA decoder (src/dep/libs/lib7z, lzma)\n\n" + read(LIBS / "lzma/LICENSE"),
        "libchdr, CHD images (src/dep/libs/libchdr)\n\n" + read(LIBS / "libchdr/LICENSE.txt"),
        "Zstandard, single-file decoder (src/dep/libs/zstd), under its BSD licence (the BSD-3-Clause\n"
        "text above, copyright Meta Platforms, Inc. and affiliates)\n\n" + leading_comment(LIBS / "zstd/zstddeclib.c"),
        "dr_libs: dr_flac, dr_mp3, dr_wav (src/dep/libs/dr_libs)\n\n" + read(LIBS / "dr_libs/LICENSE.txt"),
        "stb_vorbis (src/dep/libs/stb_vorbis)\n\n" + stb_vorbis_licence(),
        "r8brain-free-src, the resampler (src/dep/libs/r8brain)\n\n" + r8brain_licence(),
        "libspng, PNG decoding (src/dep/libs/libspng; https://libspng.org), BSD-2-Clause, with parts\n"
        "derived from libpng under the libpng licence\n\n" + read(lics / "BSD-2-Clause.txt") + RULE.lstrip("\n")
        + read(lics / "libpng-2.0.txt"),
        "PlutoSVG (src/dep/libs/plutosvg)\n\n" + read(LIBS / "plutosvg/LICENSE-plutosvg"),
        "PlutoVG (src/dep/libs/plutosvg)\n\n" + read(LIBS / "plutosvg/LICENSE-plutovg"),
        "PlutoVG's rasteriser and stroker, from FreeType (src/dep/libs/plutosvg/plutovg-ft-*)\n\n"
        + read(LIBS / "plutosvg/FTL.TXT"),
        "uGUI, the core's message screen (src/burner/libretro/deps/ugui)\n\n" + read(lics / "LicenseRef-uGUI.txt"),
        "Source Han Sans, the font of that screen (deps/ugui/SourceHanSansCN_Medium_13X17.c)\n\n"
        + read(LIBRETRO / "deps/ugui/LICENSE.md").split("###  µGUI License")[0].split("\n", 2)[2],
        "libretro-common (src/burner/libretro/libretro-common), under the MIT licence\n\n"
        + leading_comment(LIBRETRO / "libretro-common/file/file_path.c"),
        sdk_notices,
        "picolibc, the C library of the NBT toolchain's runtime, linked statically "
        "(https://github.com/picolibc/picolibc)\n\n"
        + read(runtime / "COPYING.picolibc") + RULE.lstrip("\n")
        + "picolibc's newlib-derived parts\n\n" + read(runtime / "COPYING.NEWLIB"),
    ]
    text = "\n\n" + RULE.join(p.rstrip("\n") + "\n" for p in parts)
    (ROOT / "legal").mkdir(exist_ok=True)
    (ROOT / "legal/NOTICE.txt").write_text(text, encoding="utf-8")
    print(f"legal/NOTICE.txt: {len(parts)} sections")


if __name__ == "__main__":
    main()
