<!-- SPDX-License-Identifier: MPL-2.0 -->
# License notices

The repository's original work is licensed as described in its root README and LICENSE. Third-party components retain their own licenses and copyright notices, collected in [NOTICE.txt](NOTICE.txt) (written by `make notice`, `tools/make_notice.py`). Original NBTFoundry artwork is MPL-2.0.

| Component | Licence | Text |
| --- | --- | --- |
| This application (`src/`, `tests/`, `tools/`, build files) | MPL-2.0 | [LICENSE](../LICENSE) |
| FinalBurn Neo (`third_party/fbneo`) | FinalBurn Neo's licence (non-commercial, no donations), and the MAME License it is subject to | [LicenseRef-FBNeo](../LICENSES/LicenseRef-FBNeo.txt), [LicenseRef-MAME](../LICENSES/LicenseRef-MAME.txt) |
| FinalBurn Neo's files tagged `license:BSD-3-Clause` or `MIT` | BSD-3-Clause, MIT | [BSD-3-Clause](../LICENSES/BSD-3-Clause.txt), [MIT](../LICENSES/MIT.txt); holders in NOTICE.txt |
| HuC6280 PSG, YMF278B sound chips | LGPL-2.1-or-later (YMF278B: or the MAME License) | [LGPL-2.1-or-later](../LICENSES/LGPL-2.1-or-later.txt) |
| Z180, uPD7810 CPU cores | MAME License or GPL-2.0-or-later | [GPL-2.0-or-later](../LICENSES/GPL-2.0-or-later.txt) |
| zlib, Minizip | Zlib | [Zlib](../LICENSES/Zlib.txt); NOTICE.txt |
| LZMA SDK | public domain | NOTICE.txt |
| libchdr, Zstandard | BSD-3-Clause | NOTICE.txt |
| dr_libs | Unlicense or MIT-0 | [MIT-0](../LICENSES/MIT-0.txt) |
| stb_vorbis, r8brain-free-src, PlutoSVG, PlutoVG, libretro-common | MIT (stb_vorbis: or public domain) | [MIT](../LICENSES/MIT.txt); NOTICE.txt |
| libspng | BSD-2-Clause, with libpng-2.0 parts | [BSD-2-Clause](../LICENSES/BSD-2-Clause.txt), [libpng-2.0](../LICENSES/libpng-2.0.txt) |
| PlutoVG's FreeType-derived rasteriser | FTL | [FTL](../LICENSES/FTL.txt) |
| µGUI | its own permissive terms | [LicenseRef-uGUI](../LICENSES/LicenseRef-uGUI.txt) |
| Source Han Sans (a bitmap of it, the core's message font) | OFL-1.1 | [OFL-1.1](../LICENSES/OFL-1.1.txt) |
| NBT App SDK and its third-party parts | MPL-2.0; MIT, public domain | [MPL-2.0](../LICENSES/MPL-2.0.txt); NOTICE.txt |
| picolibc (the NBT toolchain's C library, linked in) | BSD-style | NOTICE.txt |
| compiler-rt, libc++, libc++abi, libunwind (linked in) | Apache-2.0 WITH LLVM-exception | no attribution owed in binaries |

The notices are a snapshot of the current dependencies. Update them when changing the pin, a bundled dependency or the toolchain. FinalBurn Neo's licence forbids any monetary gain from it and asks that changes to its source be made public: the package is distributed free of charge only, with this repository, its submodule and the SDK commit it names (`release/sdk.ref`) as its source.

No ROM image, game or BIOS is included or distributed.

See [DISCLAIMER.md](../DISCLAIMER.md) for head-unit risks and warranty and liability terms.
