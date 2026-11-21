// SPDX-License-Identifier: MPL-2.0
/* The game list's entries: a romset archive named by FinalBurn Neo's title
 * for it. */
#ifndef NBT_FBNEO_GAMES_HPP
#define NBT_FBNEO_GAMES_HPP

#include <stddef.h>

namespace fbneo {

/* For the SDK's libretro host (HostConfig::describe), with the core
 * initialised: the label of the file `name` ("mslug.zip"), at most size - 1
 * bytes, from the driver of that romset ("Metal Slug - Super Vehicle-001",
 * with "(not working)" for one FinalBurn Neo cannot run). False leaves the
 * entry out of the list: a BIOS or device set (BDF_BOARDROM: "neogeo.zip",
 * "pgm.zip"), which games use but which cannot start. A file named after no
 * driver keeps its name. */
bool describe_game(const char* name, char* label, size_t size);

}  // namespace fbneo

#endif /* NBT_FBNEO_GAMES_HPP */
