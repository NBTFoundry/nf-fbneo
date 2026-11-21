// SPDX-License-Identifier: MPL-2.0
#include "controls.hpp"

#include <stddef.h>

#include "libretro.h"
#include "nbt/app/video.hpp"

namespace fbneo {

namespace {

using nbt::frontend::Binding;
using nbt::frontend::ControllerProfile;
using nbt::frontend::KeyboardProfile;
using nbt::frontend::PadProfile;
using nbt::frontend::Profiles;

/* NBT_GAMEPAD_* name buttons by position, so one layout serves every family:
 * Xbox A and DualShock Cross are the bottom button, B, where FinalBurn Neo's
 * "Classic" RetroPad puts a game's first button. The stick clicks are L3 and
 * R3 (a few games' extra buttons). */
const Binding kPadButtons[] = {{NBT_GAMEPAD_SOUTH, RETRO_DEVICE_ID_JOYPAD_B},
                               {NBT_GAMEPAD_EAST, RETRO_DEVICE_ID_JOYPAD_A},
                               {NBT_GAMEPAD_WEST, RETRO_DEVICE_ID_JOYPAD_Y},
                               {NBT_GAMEPAD_NORTH, RETRO_DEVICE_ID_JOYPAD_X},
                               {NBT_GAMEPAD_LB, RETRO_DEVICE_ID_JOYPAD_L},
                               {NBT_GAMEPAD_RB, RETRO_DEVICE_ID_JOYPAD_R},
                               {NBT_GAMEPAD_LS, RETRO_DEVICE_ID_JOYPAD_L3},
                               {NBT_GAMEPAD_RS, RETRO_DEVICE_ID_JOYPAD_R3},
                               {NBT_GAMEPAD_VIEW, RETRO_DEVICE_ID_JOYPAD_SELECT},
                               {NBT_GAMEPAD_MENU, RETRO_DEVICE_ID_JOYPAD_START},
                               {NBT_GAMEPAD_UP, RETRO_DEVICE_ID_JOYPAD_UP},
                               {NBT_GAMEPAD_DOWN, RETRO_DEVICE_ID_JOYPAD_DOWN},
                               {NBT_GAMEPAD_LEFT, RETRO_DEVICE_ID_JOYPAD_LEFT},
                               {NBT_GAMEPAD_RIGHT, RETRO_DEVICE_ID_JOYPAD_RIGHT}};

/* The left stick is the D-pad (an arcade stick), the triggers L2 and R2.
 * View and Menu held together (Share/Create and Options: Coin and Start), or
 * the Xbox or PS button, open the emulator's menu. */
const PadProfile kPad = {kPadButtons,
                         sizeof(kPadButtons) / sizeof(kPadButtons[0]),
                         RETRO_DEVICE_ID_JOYPAD_UP,
                         RETRO_DEVICE_ID_JOYPAD_DOWN,
                         RETRO_DEVICE_ID_JOYPAD_LEFT,
                         RETRO_DEVICE_ID_JOYPAD_RIGHT,
                         RETRO_DEVICE_ID_JOYPAD_L2,
                         RETRO_DEVICE_ID_JOYPAD_R2,
                         NBT_GAMEPAD_VIEW | NBT_GAMEPAD_MENU,
                         NBT_GAMEPAD_GUIDE};

/* The iDrive controller: push is the first button (B) and a BACK tap the
 * second (A), tilts the stick, the favourite keys 1 to 4 the third to sixth
 * (Y, X, L, R: Neo Geo C and D, a six-button game's top row and last kick),
 * the knob L2 and R2, MEDIA Coin, OPTION Start. MENU or a BACK hold opens the
 * menu, a long hold quits. */
const Binding kControllerKeys[] = {{NBT_CONTROLLER_PUSH, RETRO_DEVICE_ID_JOYPAD_B},
                                   {NBT_CONTROLLER_TILT_UP, RETRO_DEVICE_ID_JOYPAD_UP},
                                   {NBT_CONTROLLER_TILT_DOWN, RETRO_DEVICE_ID_JOYPAD_DOWN},
                                   {NBT_CONTROLLER_TILT_LEFT, RETRO_DEVICE_ID_JOYPAD_LEFT},
                                   {NBT_CONTROLLER_TILT_RIGHT, RETRO_DEVICE_ID_JOYPAD_RIGHT},
                                   {NBT_CONTROLLER_MEDIA, RETRO_DEVICE_ID_JOYPAD_SELECT},
                                   {NBT_CONTROLLER_OPTION, RETRO_DEVICE_ID_JOYPAD_START},
                                   {NBT_CONTROLLER_FAVOURITE(0), RETRO_DEVICE_ID_JOYPAD_Y},
                                   {NBT_CONTROLLER_FAVOURITE(1), RETRO_DEVICE_ID_JOYPAD_X},
                                   {NBT_CONTROLLER_FAVOURITE(2), RETRO_DEVICE_ID_JOYPAD_L},
                                   {NBT_CONTROLLER_FAVOURITE(3), RETRO_DEVICE_ID_JOYPAD_R}};
const ControllerProfile kController = {kControllerKeys,
                                       sizeof(kControllerKeys) / sizeof(kControllerKeys[0]),
                                       RETRO_DEVICE_ID_JOYPAD_L2,
                                       RETRO_DEVICE_ID_JOYPAD_R2,
                                       150,
                                       RETRO_DEVICE_ID_JOYPAD_A,
                                       NBT_CONTROLLER_MENU};

/* The desktop: the arrows, Z B, X A, A Y, S X, Q L, W R, E L2, R R2 (the
 * buttons by position as on a pad), Return Start, Right Shift Coin; Escape
 * the menu. */
const Binding kKeys[] = {{'z', RETRO_DEVICE_ID_JOYPAD_B},
                         {'x', RETRO_DEVICE_ID_JOYPAD_A},
                         {'a', RETRO_DEVICE_ID_JOYPAD_Y},
                         {'s', RETRO_DEVICE_ID_JOYPAD_X},
                         {'q', RETRO_DEVICE_ID_JOYPAD_L},
                         {'w', RETRO_DEVICE_ID_JOYPAD_R},
                         {'e', RETRO_DEVICE_ID_JOYPAD_L2},
                         {'r', RETRO_DEVICE_ID_JOYPAD_R2},
                         {nbt::app::kHostKeyReturn, RETRO_DEVICE_ID_JOYPAD_START},
                         {nbt::app::kHostKeyRightShift, RETRO_DEVICE_ID_JOYPAD_SELECT},
                         {nbt::app::kHostKeyUp, RETRO_DEVICE_ID_JOYPAD_UP},
                         {nbt::app::kHostKeyDown, RETRO_DEVICE_ID_JOYPAD_DOWN},
                         {nbt::app::kHostKeyLeft, RETRO_DEVICE_ID_JOYPAD_LEFT},
                         {nbt::app::kHostKeyRight, RETRO_DEVICE_ID_JOYPAD_RIGHT}};
const KeyboardProfile kKeyboard = {kKeys, sizeof(kKeys) / sizeof(kKeys[0]),
                                   nbt::app::kHostKeyEscape};

const Profiles kProfiles = {{&kPad, &kPad, &kPad, &kPad}, &kController, &kKeyboard};

}  // namespace

const nbt::frontend::Profiles& controls() {
  return kProfiles;
}

}  // namespace fbneo
