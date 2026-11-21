// SPDX-License-Identifier: MPL-2.0
/* An arcade panel on a USB gamepad, the iDrive controller and the desktop
 * keyboard. */
#ifndef NBT_FBNEO_CONTROLS_HPP
#define NBT_FBNEO_CONTROLS_HPP

#include "nbt/frontend/pad_profiles.hpp"

namespace fbneo {

/* Each pad family plays as FinalBurn Neo's "Classic" RetroPad, button for
 * button by position: actions are RETRO_DEVICE_ID_JOYPAD_* of port 0. The
 * core lays a game's buttons out on them: Neo Geo A, B, C, D on the bottom,
 * right, left and top face buttons (B, A, Y, X); a six-button game's top row
 * on Y, X, L and its bottom row on B, A, R; Coin on Select, Start on Start. */
const nbt::frontend::Profiles& controls();

}  // namespace fbneo

#endif /* NBT_FBNEO_CONTROLS_HPP */
