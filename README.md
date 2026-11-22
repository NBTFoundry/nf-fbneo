<!-- SPDX-License-Identifier: MPL-2.0 -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/logo-dark.svg">
    <img src="docs/assets/logo-light.svg" alt="NBTFoundry" height="44">
  </picture>
</p>

<h1 align="center">FinalBurn Neo for NBT Manager</h1>

> **Warning: installing or modifying this software can brick your head unit. Recovery may require professional service or replacement, at your expense. Provided AS IS; use at your own risk, subject to applicable law.** [Read the risk and liability disclaimer](DISCLAIMER.md).

<p align="center">
  <b>Arcade games on the iDrive screen,</b><br>
  played with a USB gamepad laid out like an arcade panel, or the iDrive controller.
</p>

FinalBurn Neo's libretro core, with one change for the car (`patches/`), on the NBT App SDK's libretro host:
Neo Geo, CPS-1, CPS-2, CPS-3 and thousands of other arcade boards, the frame
scaled to the car's panel (vertical games turned upright), sound through the
car's speakers, NVRAM saves, save states and a pause menu. Romsets stay zipped,
as FinalBurn Neo reads them; they come from a USB stick or the NBT Manager phone
app, copied to the head unit's hard disk. Installed and launched through NBT
Manager.

**Supported head units:** BMW NBT Evo (iDrive 6). Support for the earlier NBT
may come later.

Part of [NBTFoundry](https://github.com/NBTFoundry):
[manager](https://github.com/NBTFoundry/manager) ·
[sdk](https://github.com/NBTFoundry/sdk) ·
[mobile-app](https://github.com/NBTFoundry/mobile-app) ·
[installer](https://github.com/NBTFoundry/installer) ·
[toolchains](https://github.com/NBTFoundry/toolchains)

Not affiliated with or endorsed by BMW AG or the FinalBurn Neo team. BMW, iDrive
and NBT are trademarks of BMW AG; Neo Geo is a trademark of SNK Corporation, CPS
and Capcom of Capcom Co., Ltd. No ROM image, game or BIOS is included: use only
romsets you have the right to use.

## Status

Built and tested on the desktop and in the SDK's VM under QEMU; not yet tested
in a car.

## Adding games

FinalBurn Neo plays **romsets**: one `.zip` (or `.7z`) archive per game, named
after FinalBurn Neo's name for it (`mslug.zip`, `sf2ce.zip`), holding the ROM
files that version of FinalBurn Neo expects (matched by CRC, any file names). A
clone needs its parent's archive too (`sf2ce.zip` with `sf2.zip`), and a board
its BIOS set: `neogeo.zip` for Neo Geo games, `pgm.zip`, `decocass.zip`,
`isgsm.zip` and so on. Build romsets for the FinalBurn Neo version in this
package with a ROM manager (ClrMamePro, RomVault) and the DAT files at
[libretro/FBNeo/dats](https://github.com/libretro/FBNeo/tree/master/dats)
(upstream's `src/burner/libretro/README.md`, "Building romsets for FBNeo"). Archives of up
to 512 MiB each, 16 GiB in all (NBT Manager's `files` capability).

- **From a USB stick** (most romsets): on the car, hold the push on FinalBurn
  Neo in NBT Manager, then **Files** › **Import from a USB stick**: every
  archive on the stick (in folders too) is listed, one or all of them copied
  to the car as they are, unopened.
- **From the phone:** archives up to 64 MiB: the NBT Manager app, the car,
  FinalBurn Neo, **Files**, **Add files**.

The game list names each game by FinalBurn Neo's title for it ("Metal Slug -
Super Vehicle-001"), in title order, with "(not working)" for a set FinalBurn
Neo knows but cannot run. BIOS and device sets are used but not listed; an
archive FinalBurn Neo does not know is listed by its file name.

Not available here yet: console and computer games (FinalBurn Neo finds them by
folder, `nes/smb.zip`, which the files folder does not have), Neo Geo CD and
other disc-based systems, sample sets and `hiscore.dat` (they live in
sub-folders of FinalBurn Neo's system folder).

## Playing

FinalBurn Neo opens on its game list, the last game played focused. In a game,
the pause menu has Resume, Save state, Load state, the slot (1 to 4), Reset,
Choose another game and Quit. NVRAM and EEPROM saves are written when they
change and on leaving; they and the states stay in FinalBurn Neo's data folder
across updates.

## Controls

Bindings are chosen for the pad plugged in, by its family; there is nothing to
set. Buttons are where an arcade panel and FinalBurn Neo's "Classic" layout put
them: a game's first button is the bottom face button, Neo Geo A, B, C, D the
bottom, right, left and top ones, a six-button fighter's punches the left, top
and left shoulder, its kicks the bottom, right and right shoulder.

| FinalBurn Neo (RetroPad) | Xbox | DualShock 4 / DualSense | iDrive controller | Desktop |
| --- | --- | --- | --- | --- |
| Stick | D-pad or left stick | D-pad or left stick | Tilt | Arrows |
| B (button 1, Neo Geo A) | A | Cross | Push | Z |
| A (button 2, Neo Geo B) | B | Circle | BACK, tap | X |
| Y (button 3, Neo Geo C) | X | Square | Favourite key 1 | A |
| X (button 4, Neo Geo D) | Y | Triangle | Favourite key 2 | S |
| L / R (buttons 6 / 5) | LB / RB | L1 / R1 | Favourite keys 3 / 4 | Q / W |
| L2 / R2 | LT / RT | L2 / R2 | Turn the knob left / right | E / R |
| Coin | View | Share / Create | MEDIA | Right Shift |
| Start | Menu | Options | OPTION | Return |
| Pause menu | Xbox button, or View + Menu | PS button, or Share / Create + Options | MENU, or BACK held | Escape |
| Quit | from the menu | from the menu | BACK, long hold | from the menu |

In the menus the D-pad, left stick, knob or tilts move, the bottom button
(push) chooses and the right button (BACK) goes back; LB and RB (L1, R1) jump
ten games. The menus name the buttons of the pad in use, and a notice says
when a pad is plugged in or removed: the iDrive controller then plays. The
knob holds L2 or R2 for 150 ms per detent. Which pads are supported is up to
NBT Manager (`NBTFoundry/manager: docs/gamepad-bridge.md`).

## Settings

Changed from the phone app or NBT Manager's settings page; they apply at once.

| Setting | Choices | Default |
| --- | --- | --- |
| Aspect | 4-3 (the game's screen, 3:4 when vertical), pixel (whole multiples), full | 4-3 |
| Filter | sharp (crisp pixels, smoothed edges), smooth, nearest | sharp |
| Neo Geo | auto (the BIOS DIP switch), mvs (arcade), aes (home console), unibios | auto |
| CPU clock | 80, 90, 100, 110, 120 (% of the emulated CPUs' clock) | 100 |
| Frame skip | off, auto (while running late), 1, 2 | off |
| Sound | on, off | on |
| Show FPS | off, on | off |
| Debug log | off, on | off |

Neo Geo modes need their BIOS in `neogeo.zip` (UniBIOS: its files added to it).
Per-game DIP switches are not offered.

## Bridge

The package carries the guest (built with the NBT toolchain, run by NBT
Manager's `nbt-runner`) and declares bridge 1.7: `show`, `controller`, `files`
and `runner` required, `status`, `live-settings` and `gamepad` optional, and
the files policy `zip,7z|512|16384`. It also carries what the phone app shows
before an install (the FinalBurn Neo version, the project, the licence,
notices), so it needs NBT Manager 0.3.1 or later. FinalBurn Neo reports the game played as
its status. NBT Manager keeps its standard error as its log (shown, shared and
cleared from the phone app); the Debug log setting adds tracing and the core's
debug messages.

## Build

Needs the NBT App SDK next to this repository (`../sdk`, or `NBT_SDK_DIR`), gcc,
GNU make 4.3 or newer, Python 3, and the X11, EGL and GLESv2
development files; Xvfb for the tests. `git submodule update --init` fetches
FinalBurn Neo (shallow).

```sh
make -j"$(nproc)" host test test-asan check-static-init   # host binary and tests
./build/nbt-fbneo-host                                    # play on the desktop (X11)
```

The desktop build lists the romsets in `NBT_FILES_DIR` and keeps saves in
`NBT_DATA_DIR` (the current folder without it):
`NBT_FILES_DIR=~/arcade NBT_DATA_DIR=/tmp/fbneo ./build/nbt-fbneo-host`, or
`--game <file>` to start one directly. The tests make a romset of their own:
the Space Invaders board's four ROMs hold a small 8080 program, each file
given the CRC-32 the driver expects (read from upstream's driver source); no
game is needed.

Head unit: FinalBurn Neo holds LGPL code (two sound chips), so the application
is a **guest** (`sdk/docs/native-apps.md`): built with the NBT toolchain (`make
-C ../sdk toolchain` once) and run as its own process by the `nbt-runner` NBT
Manager ships (bridge 1.7, `runner`).

```sh
make -j"$(nproc)" guest                                  # build/nbt-fbneo.guest
make APP_KEY=/path/to/apps-signing-key.pem package       # build/fbneo-<version>.nbt
make vm-test                                             # the SDK's VM under QEMU
```

The guest is linked with its symbols (`build/unstripped/`, with its link map,
for crash addresses) and shipped stripped: every driver is in it, about 42 MiB
of the 64 MiB a package holds. `package` signs it with NBT Manager's packer
(`../manager/tools/package.py`, or `NBT_MGR_DIR`), described by
`release/package.args`; `make package-args` writes the FinalBurn Neo version the
pin builds, and `make test` fails when it lags. `vm-test` runs it in the SDK's
VM, with the SDK's own `nbt-runner` (`sdk/docs/native-apps.md`, "Testing without
a head unit", says what building it takes). `make notice` writes
`legal/NOTICE.txt`.

### FinalBurn Neo on the NBT toolchain

Upstream's own libretro Makefile (`src/burner/libretro/Makefile`, every driver:
its default subset) builds the core, unchanged, in a copy of the submodule's
`src/` per build kind under `build/core/` (upstream writes its objects next to
its sources); `tools/core.mk`, read after it, archives upstream's object list
into a static library and records its defines and include folders for
`src/games.cpp`, which reads FinalBurn Neo's driver table. The guest uses the
C 68000 core (no Cyclone: its assembly relies on unaligned access, which
guests leave off until the car session settles it), no NEON, and one flag after
upstream's own: C++11 (libc++ does not build as C++03 with picolibc's
`_Static_assert`).

## Releases

`.github/workflows/ci.yml` runs the host tests, the same under ASan/UBSan and
the guest build on every push and pull request. A `vX.Y.Z` tag runs
`.github/workflows/release.yml`: NBT Manager's application release workflow
builds the guest on a plain runner with the NBT toolchain (no private image),
signs it with the apps key after a maintainer approves the run (the `release`
environment, secret `APPS_SIGNING_KEY`, tags `v*` only) and publishes
`fbneo-X.Y.Z.nbt`, sequence `X*1000000 + Y*1000 + Z`. `release/sdk.ref` is the
SDK commit both build against: [SDK
0.1.0](https://github.com/NBTFoundry/sdk/releases/tag/v0.1.0).

## To confirm on the head unit

- Full speed with sound (Show FPS) for Neo Geo and CPS-2 games: otherwise
  Frame skip, then the CPU clock (`port-perf`).
- Large romsets (CPS-3, Neo Geo's biggest) within the 256 MiB a guest may use.
- Vertical games upright and at their aspect.
- The profile follows a pad plugged in and out; the iDrive controller plays
  without one.

## Layout

| Path | Contents |
| --- | --- |
| `third_party/fbneo/` | FinalBurn Neo's libretro port (libretro/FBNeo), unmodified (submodule) |
| `patches/` | Applied to the build's copy of its sources: `m68000-aligned-longs.patch` (a 68000 long at an address not a multiple of 4 goes byte by byte; the car stops a misaligned 32-bit load with SIGBUS) |
| `src/main.cpp` | The application: the SDK's libretro host with FinalBurn Neo's settings |
| `src/games.*` | The game list's titles from FinalBurn Neo's driver table; BIOS sets left out |
| `src/controls.*` | The arcade layout for each pad family, the iDrive controller and the keyboard |
| `tests/` | Controls unit test (`controls_test.cpp`), play and package tests (`test_fbneo.py`) |
| `tools/` | `core.mk` (upstream's objects into a library); FinalBurn Neo's version for the package (`package_version.py`); notices (`make_notice.py`) |
| `release/` | The package description and the SDK commit to build against |

## License

Copyright (c) 2026 Fabien Poussin. Original code, tests, build scripts and
documentation are licensed under **MPL-2.0**; see [LICENSE](LICENSE).

FinalBurn Neo keeps its own licence
([LICENSES/LicenseRef-FBNeo.txt](LICENSES/LicenseRef-FBNeo.txt)), which also
binds it to the MAME License
([LICENSES/LicenseRef-MAME.txt](LICENSES/LicenseRef-MAME.txt)): no sale, lease
or rent, no monetary gain of any kind, no donations for work using it, changes
to its source made public. The application's binary contains it and may be
distributed only on those terms, free of charge. Parts of FinalBurn Neo and the
libraries it bundles have their own licences (LGPL-2.1, BSD, MIT, zlib, OFL and
others). Original NBTFoundry logos and artwork are MPL-2.0; copyright
permission for artwork does not grant trademark rights or imply endorsement by
BMW AG or the FinalBurn Neo team.

See [legal/README.md](legal/README.md) for third-party license notices.
