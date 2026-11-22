<!-- SPDX-License-Identifier: MPL-2.0 -->
# Car test: FinalBurn Neo before a release

Parked, ignition on. About 45 minutes, all from the phone: no adapter, no
computer.

Run it on a candidate before tagging a release, and whenever the car-side
behaviour changed. FinalBurn Neo's libretro core with every arcade driver is a
**guest**, run by the `nbt-runner` NBT Manager ships (bridge 1.7). Romsets stay
zipped: the car keeps the archives as they are and the core reads them. The
main questions: Neo Geo and CPS-2 games at full speed with sound, vertical
games upright, large romsets within the memory an application may use.

## You need

- NBT Manager 0.3.1 or later on the car, and its phone app, paired.
- From the kit folder: the candidate `fbneo-<version>.nbt`, a second one with a
  higher sequence for part C, and their `SHA256SUMS` file. Add both to the
  phone app's library.
- A USB stick with romsets you own, built for a recent FinalBurn Neo (DATs:
  github.com/libretro/FBNeo, `dats/`), zipped, loose or in folders:
  - a **Neo Geo** game (`mslug.zip`, `kof98.zip`…) and **`neogeo.zip`**;
  - a **CPS-2** game (`sfa3.zip`, `ddsom.zip`…; a clone with its parent);
  - a **vertical** game (`1942.zip`, `galaga.zip`, `dsmbl.zip`…);
  - if you have one, a large set (CPS-3 `sfiii3.zip`, or `kof2003.zip`).
- A USB gamepad (Xbox or DualShock 4 / DualSense), for part B.5.

## A. Install, health check, settings

| # | Do | Look for |
| --- | --- | --- |
| A0 | Phone: Library › open the candidate | Under the file name: **FinalBurn Neo** (version and commit), **Project: FinalBurn Neo (https://github.com/libretro/FBNeo)**, **Licence: FinalBurn Neo licence (non-commercial)**, then the text, ending with the repository's address |
| A1 | Phone: Car › FinalBurn Neo › install (or update to) the candidate; approve on the car | The health check passes (about 10 s), "Installed" |
| A2 | Car: hold the push on **fbneo** › settings | 8 settings: Aspect, Filter, Neo Geo, CPU clock, Frame skip, Sound, Show FPS, Debug log |
| A3 | Set **Show FPS: on**, **Debug log: on** | Kept when you leave and come back |

## B. Romsets, start and play

| # | Do | Look for |
| --- | --- | --- |
| B1 | Plug in the stick. Hold the push on **fbneo** › **Files** › **Import from a USB stick** | Every `.zip` on the stick listed **as one file each** (not opened); Import all |
| B2 | Files page | The archives with their sizes, the same as on the stick |
| B3 | Select **fbneo** | The list shows titles ("Metal Slug - Super Vehicle-001"), in title order; **no `neogeo.zip`** entry |
| B4 | Start the Neo Geo game | Title screen with **sound**; FPS top right about 59 |
| B5 | Controls, iDrive: tilts the stick, push button A, BACK tap B, favourite keys 1–4 C, D and the last two buttons, MEDIA coin, OPTION start. Then plug the pad: a notice names it; A/B/X/Y (Cross/Circle/Square/Triangle) are Neo Geo A/B/C/D. Unplug it | Every button reacts; the iDrive controller plays again after unplugging |
| B6 | Pause menu (MENU, BACK hold, or the pad's Xbox/PS button): **Save state**, play on, **Load state** | Back where saved |
| B7 | **Choose another game** › the CPS-2 game | Plays with sound; note the FPS in play |
| B8 | The vertical game | **Upright**, a tall picture in the middle of the screen, not lying on its side |
| B9 | The large set, if you have one | Starts, or a clear notice; note which |
| B10 | Settings while a game runs: **Aspect: full**, **Filter: smooth** (each applies at once); **Neo Geo: aes**, then pause menu › Choose another game › the Neo Geo game again | The home-console version of its title screen |
| B11 | If a game ran under full speed: **Frame skip: auto**, then **CPU clock: 90** | FPS and sound with each |

## C. Stop, start again, update

| # | Do | Look for |
| --- | --- | --- |
| C1 | Hold the push on **fbneo** › **Stop** | Back to iDrive |
| C2 | Start it again | The list focuses the last game played |
| C3 | While a game runs, phone: update to the second package; approve | It stops, checks, installs; start again: states still there |

## Logs (before switching off: `/dev/shmem` is RAM)

- Phone: **fbneo** › **Show log** › Share. Wanted lines: `game <set>.zip:
  …, aspect …, N quarter turns` for each game, `runner: … frames presented`,
  any `runner: GL error`, `guest killed by signal`, or the core's
  `[FBNeo] …` errors (a missing ROM names it).
- Phone: Car › Manage › **Manager log** and **iDrive log**.

## Going back

Uninstall **fbneo** from its page on the phone (or hold › Uninstall on the
car): its romsets go with it. Or install the last release from GitHub (a test
package with a lower sequence is refused).

## Results

| Step | OK / not OK | Notes |
| --- | --- | --- |
| A0 information shown | | |
| A1-A3 | | |
| B1-B2 import (time for the large sets) | | |
| B3 titles, no BIOS entry | | |
| B4 Neo Geo: sound, FPS | | |
| B5 controls | | |
| B6 states | | |
| B7 CPS-2: FPS | | |
| B8 vertical upright | | |
| B9 large set | | |
| B10 settings | | |
| B11 frame skip, CPU clock | | |
| C1-C3 | | |

With the games used (their set names) and the pad model.
