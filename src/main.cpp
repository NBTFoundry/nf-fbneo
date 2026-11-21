// SPDX-License-Identifier: MPL-2.0
/* FinalBurn Neo on NBT Manager: the upstream libretro core, linked
 * statically, on the SDK's libretro host (game list, saves, states, pause
 * menu, controls). */
#include <stddef.h>

#include "controls.hpp"
#include "games.hpp"
#include "nbt/retro/host.hpp"

namespace {

/* The games offered: romsets, zipped as FinalBurn Neo expects them (one
 * archive per set, named after it). BIOS and device sets sit beside the
 * games, where the core looks for them (the files folder is its system
 * folder), and are left out of the list (games.cpp). */
const char* const kExtensions[] = {"zip", "7z", NULL};

/* Manager settings feeding the core's variables
 * (src/burner/libretro/retro_common.cpp): setting value, core value. */
const char* const kNeoGeo[] = {"auto",    "DIPSWITCH", "mvs",     "MVS_EUR", "aes",
                               "AES_EUR", "unibios",   "UNIBIOS", NULL};
const char* const kCpuSpeed[] = {"100", "100%", "110", "110%", "120", "120%",
                                 "90",  "90%",  "80",  "80%",  NULL};
const nbt::retro::VariableMap kVariables[] = {{"neogeo", "fbneo-neogeo-mode", kNeoGeo},
                                              {"cpu_speed", "fbneo-cpu-speed-adjust", kCpuSpeed}};

}  // namespace

int main(int argc, char** argv) {
  const nbt::retro::HostConfig config = {"fbneo",
                                         "FinalBurn Neo",
                                         "Arcade",
                                         kExtensions,
                                         &fbneo::controls(),
                                         kVariables,
                                         sizeof(kVariables) / sizeof(kVariables[0]),
                                         0.0f /* the game's own (3:4 when vertical) */,
                                         0 /* the core reads its romsets itself */,
                                         true /* BIOS sets with the games */,
                                         NULL /* each game one archive */,
                                         &fbneo::describe_game};
  return nbt::retro::run(argc, argv, config);
}
