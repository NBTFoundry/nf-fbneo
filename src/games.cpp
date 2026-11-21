// SPDX-License-Identifier: MPL-2.0
#include "games.hpp"

#include <stdio.h>
#include <string.h>

/* FinalBurn Neo's driver table (src/burn/burn.h, through its front-end
 * header): built with upstream's include paths and defines (Makefile). */
#include "burner.h"

namespace fbneo {

bool describe_game(const char* name, char* label, size_t size) {
  if (!name || !label || !size) return false;
  char set[100];
  snprintf(set, sizeof(set), "%s", name);
  char* dot = strrchr(set, '.');
  if (dot) *dot = '\0';
  /* FinalBurn Neo's driver names are lower case, as are the archives. */
  const INT32 index = BurnDrvGetIndex(set);
  if (index < 0) {
    snprintf(label, size, "%s", name);
    return true;
  }
  /* The driver queries read the active driver: none while the list shows. */
  const UINT32 active = nBurnDrvActive;
  nBurnDrvActive = static_cast<UINT32>(index);
  const bool board = (BurnDrvGetFlags() & BDF_BOARDROM) != 0;
  const char* title = BurnDrvGetTextA(DRV_FULLNAME);
  const bool working = BurnDrvIsWorking();
  if (!board) {
    snprintf(label, size, "%s%s", title && title[0] ? title : set, working ? "" : " (not working)");
  }
  nBurnDrvActive = active;
  return !board;
}

}  // namespace fbneo
