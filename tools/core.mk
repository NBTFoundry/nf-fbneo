# SPDX-License-Identifier: MPL-2.0
# Read after FinalBurn Neo's own libretro Makefile
# (make -f Makefile -f core.mk nbt-core, in src/burner/libretro of a copy of
# upstream's src/): upstream's object list (OBJS), built by upstream's rules
# and flags, archived into NBT_CORE_LIB for a static link.
#
# NBT_CORE_CFLAGS and NBT_CORE_CXXFLAGS come after upstream's own flags (its
# -std, for one), where the environment's CFLAGS and CXXFLAGS come before.
CFLAGS += $(NBT_CORE_CFLAGS)
CXXFLAGS += $(NBT_CORE_CXXFLAGS)

# The list is too long for one command line: the archiver reads it from a file.
# Beside the library, <library>.flags: upstream's defines and include folders
# (as system folders), for our sources that use its headers.
.PHONY: nbt-core
nbt-core: $(OBJS)
	$(file >$(NBT_CORE_LIB).in,$(OBJS))
	rm -f $(NBT_CORE_LIB)
	$(AR) rcs $(NBT_CORE_LIB) @$(NBT_CORE_LIB).in
	rm -f $(NBT_CORE_LIB).in
	$(file >$(NBT_CORE_LIB:.a=.flags),$(FBNEO_DEFINES) $(addprefix -isystem ,$(abspath $(INCLUDE_DIRS))))
