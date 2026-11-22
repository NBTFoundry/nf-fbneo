# SPDX-License-Identifier: MPL-2.0
SHELL := /bin/bash

BUILD_DIR ?= build
OBJ_DIR := $(BUILD_DIR)/obj

APP_VERSION ?= 0.0.1
APP_SEQ ?= 1
APP_KEY ?=
# Sibling NBTFoundry checkouts; override as needed. The SDK is built into
# $(BUILD_DIR)/sdk; the manager is only needed for packaging.
NBT_SDK_DIR ?= ../sdk
NBT_MGR_DIR ?= ../manager
# The QNX SDP builds only the SDK's nbt-runner, for the VM test: FinalBurn
# Neo holds LGPL code, so the application is a guest, never a QNX build. On
# the car, NBT Manager's own nbt-runner runs the guest (bridge 1.7, runner).
QNX_ENV ?=
QNX_SCREEN_LIBDIR ?=

CC ?= gcc
CXX ?= g++

NBT_SDK_BUILD_DIR := $(abspath $(BUILD_DIR))/sdk
include $(NBT_SDK_DIR)/nbt-sdk.mk
# Each kind of object rebuilds when its compile command changes (the SDK's
# nbt-stamp.mk; the stamps are written at the end of this file).
stamp = $(OBJ_DIR)/$(1).stamp
ifeq ($(value nbt_stamp),)
$(error $(NBT_SDK_ROOT) has no nbt-stamp.mk: update that SDK checkout)
endif

# --- FinalBurn Neo: built by upstream's own libretro Makefile, unmodified ---
# Upstream writes its objects next to its sources, so each build kind gets a
# copy of the submodule's src/ under $(BUILD_DIR)/core/<kind>/ (objects kept
# between runs), where upstream's make builds them and tools/core.mk archives
# them (upstream's object list) into a static library. Flags reach it through
# the environment: upstream appends to CFLAGS and CXXFLAGS. GIT_DIR gives its
# version string the submodule's commit.
CORE_SRC := third_party/fbneo
CORE_GIT_DIR := $(shell git -C $(CORE_SRC) rev-parse --absolute-git-dir 2>/dev/null)
CORE_LIB_NAME := libfbneo.a
# Every driver (upstream's default subset, "all"), the C 68000 core (no
# Cyclone: Thumb-free ARM state, no unaligned access), no NEON.
CORE_MAKE_ARGS := platform=unix fpic= USE_CYCLONE=0 HAVE_NEON=0
core_dir = $(BUILD_DIR)/core/$(1)
# Changes upstream's sources need on the head unit, applied to the copy:
# m68000-aligned-longs (a 68000 long at an address that is not a multiple of 4
# went through a misaligned 32-bit load, which the car stops with SIGBUS).
# A patched file keeps the time of the newer of its source and its patch, so
# applying the patches again on every build recompiles nothing.
CORE_PATCHES := $(sort $(wildcard $(abspath patches)/*.patch))
core_lib = $(abspath $(call core_dir,$(1)))/$(CORE_LIB_NAME)

# Our command line's CFLAGS and CXXFLAGS (make passes them on in MAKEFLAGS)
# would replace upstream's own instead of adding to them: they stay ours.
CORE_MAKEFLAGS = MAKEFLAGS='$(filter-out CFLAGS=% CXXFLAGS=%,$(MAKEFLAGS))'
# $(call core_build,kind): upstream's make with CORE_ENV_<kind> in its
# environment and CORE_ARGS_<kind> as arguments. When those or the toolchain
# (the kind's core stamp) changed since the copy's objects were built, they go
# first: upstream's make would keep them.
define core_build
	@mkdir -p $(call core_dir,$(1))
	@if ! cmp -s $(call stamp,core-$(1)) $(call core_dir,$(1))/.stamp \
		|| test $(call stamp,core-$(1)) -nt $(call core_dir,$(1))/.stamp; then \
		test ! -f $(call core_dir,$(1))/.stamp || echo "core $(1): build stamp changed, rebuilding it"; \
		find $(call core_dir,$(1)) -name '*.o' -delete; cp $(call stamp,core-$(1)) $(call core_dir,$(1))/.stamp; fi
	tar -C $(CORE_SRC) --exclude='*.o' --exclude='*.d' -cf - src | tar -C $(call core_dir,$(1)) -xf -
	for p in $(CORE_PATCHES); do patch -s -p1 -d $(call core_dir,$(1)) < $$p || exit 1; \
		for f in $$(sed -n 's#^+++ b/##p' $$p); do \
			if test $$p -nt $(CORE_SRC)/$$f; then r=$$p; else r=$(CORE_SRC)/$$f; fi; \
			touch -r $$r $(call core_dir,$(1))/$$f; done; done
	cd $(call core_dir,$(1))/src/burner/libretro && GIT_DIR=$(CORE_GIT_DIR) $(CORE_ENV_$(1)) $(CORE_MAKEFLAGS) $(MAKE) \
		--no-print-directory -f Makefile -f $(abspath tools/core.mk) $(CORE_MAKE_ARGS) \
		NBT_CORE_LIB=$(call core_lib,$(1)) $(CORE_ARGS_$(1)) nbt-core
endef

.PHONY: FORCE
FORCE:

# Upstream's own warnings are its business: -w after its flags.
CORE_ENV_host :=
CORE_ARGS_host := NBT_CORE_CFLAGS=-w NBT_CORE_CXXFLAGS=-w
$(call core_lib,host): FORCE
	$(call core_build,host)

# Upstream's DEBUG_ASAN builds without optimisation.
CORE_ENV_asan := CFLAGS="-fno-omit-frame-pointer" CXXFLAGS="-fno-omit-frame-pointer"
CORE_ARGS_asan := DEBUG_ASAN=1 NBT_CORE_CFLAGS=-w NBT_CORE_CXXFLAGS=-w
$(call core_lib,asan): FORCE
	$(call core_build,asan)

# The guest: the NBT toolchain's flags and runtime (sdk/module/flags.mk).
# C++11 rather than upstream's C++98: libc++ in C++03 mode does not build
# with picolibc's _Static_assert macro. DT_LNK: libretro-common's VFS names
# it; the toolchain's <sys/dirent.h> (1.1.0) has only the types the runtime
# reports (never a link), so its value never matches.
CORE_GUEST_CFLAGS := -w -DDT_LNK=10
CORE_GUEST_CXXFLAGS := -w -std=gnu++11
CORE_ENV_guest = CFLAGS="$(NBT_MOD_CFLAGS)" CXXFLAGS="$(NBT_MOD_CXXFLAGS)"
CORE_ARGS_guest = CC="$(NBT_MOD_CC)" CXX="$(NBT_MOD_CXX)" AR="$(NBT_MOD_AR)" \
	NBT_CORE_CFLAGS="$(CORE_GUEST_CFLAGS)" NBT_CORE_CXXFLAGS="$(CORE_GUEST_CXXFLAGS)"
$(call core_lib,guest): FORCE | nbt-sdk-mod
	$(call core_build,guest)

# Upstream's defines and include folders, beside each library (tools/core.mk),
# for our sources that read its headers.
core_flags = $(call core_dir,$(1))/libfbneo.flags

# --- Ours: the application on the SDK's libretro host ---
APP_SRC := src/controls.cpp src/games.cpp src/main.cpp
APP_INC := $(NBT_SDK_INC) $(NBT_SDK_LIBRETRO_INC) -Isrc
APP_CXXFLAGS := -std=c++11 -O2 -Wall -Wextra -Werror -fno-exceptions -fno-rtti $(CXXFLAGS)
app_objs = $(patsubst %.cpp,$(OBJ_DIR)/$(1)/%.o,$(APP_SRC))
# games.cpp reads FinalBurn Neo's driver table through its headers.
upstream_flags = $$(cat $(call core_flags,$(1)))

HOST_APP := $(BUILD_DIR)/nbt-fbneo-host
ASAN_APP := $(BUILD_DIR)/nbt-fbneo-asan
ASAN_FLAGS := -O1 -g -fsanitize=address -fno-omit-frame-pointer
# The core after the SDK: the libretro host calls it (GNU ld takes from an
# archive only what is already wanted).
CORE_HOST_LDLIBS := -lm -lpthread

.PHONY: all host test test-asan check-static-init format guest vm-test package notice clean

all: host test

# --- Host (Linux, X11) ---
$(OBJ_DIR)/host/src/games.o: src/games.cpp $(call core_lib,host) $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(call upstream_flags,host) -MMD -MP -c $< -o $@

$(OBJ_DIR)/host/src/%.o: src/%.cpp $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) -MMD -MP -c $< -o $@

$(HOST_APP): $(call app_objs,host) $(NBT_SDK_FRONT_HOST_LIBS) $(call core_lib,host)
	$(CXX) $(call app_objs,host) $(NBT_SDK_FRONT_HOST_LIBS) $(call core_lib,host) $(LDFLAGS) \
		$(NBT_SDK_HOST_LDLIBS) $(CORE_HOST_LDLIBS) -o $@

host: $(HOST_APP) $(BUILD_DIR)/controls-test

# --- Sanitizer build: the core under AddressSanitizer (upstream's
# DEBUG_ASAN), ours under UBSan too ---
$(OBJ_DIR)/asan/src/games.o: src/games.cpp $(call core_lib,asan) $(call stamp,asan)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined $(call upstream_flags,asan) \
		-MMD -MP -c $< -o $@

$(OBJ_DIR)/asan/src/%.o: src/%.cpp $(call stamp,asan)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined -MMD -MP -c $< -o $@

$(ASAN_APP): $(call app_objs,asan) $(NBT_SDK_FRONT_ASAN_LIBS) $(call core_lib,asan)
	$(CXX) $(ASAN_FLAGS) -fsanitize=undefined $(call app_objs,asan) $(NBT_SDK_FRONT_ASAN_LIBS) \
		$(call core_lib,asan) $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) $(CORE_HOST_LDLIBS) -o $@

# --- Tests ---
$(OBJ_DIR)/host/tests/%.o: tests/%.cpp $(call stamp,host)
	@mkdir -p $(dir $@)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) -MMD -MP -c $< -o $@

$(BUILD_DIR)/controls-test: $(OBJ_DIR)/host/tests/controls_test.o $(OBJ_DIR)/host/src/controls.o \
		$(NBT_SDK_FRONT_HOST_LIBS)
	$(CXX) $^ $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) -o $@

$(BUILD_DIR)/controls-asan: tests/controls_test.cpp src/controls.cpp src/controls.hpp \
		$(NBT_SDK_FRONT_ASAN_LIBS)
	$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined tests/controls_test.cpp \
		src/controls.cpp $(NBT_SDK_FRONT_ASAN_LIBS) $(LDFLAGS) $(NBT_SDK_HOST_LDLIBS) -o $@

test: host
	$(BUILD_DIR)/controls-test
	NBT_FBNEO_APP=$(abspath $(HOST_APP)) NBT_MGR_DIR=$(abspath $(NBT_MGR_DIR)) \
		python3 -m unittest discover -s tests -v

test-asan: $(ASAN_APP) $(BUILD_DIR)/controls-asan
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
		$(BUILD_DIR)/controls-asan
	ASAN_OPTIONS=detect_leaks=0 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
		NBT_FBNEO_APP=$(abspath $(ASAN_APP)) NBT_MGR_DIR=$(abspath $(NBT_MGR_DIR)) \
		python3 -m unittest discover -s tests -v -k Play

# Our objects only: the core's are upstream's business.
check-static-init: $(call app_objs,host)
	@set -e; \
	for obj in $^; do \
		ctors="$$(readelf -S "$$obj" | awk '/\.init_array|\.ctors/ {print $$2}')"; \
		if test -n "$$ctors"; then \
			echo "ERROR: static constructor section in $$obj: $$ctors"; exit 1; \
		fi; \
	done; \
	echo "OK: no .init_array/.ctors in our objects"
	+@$(NBT_SDK_MAKE) check-static-init

format:
	clang-format -i src/*.cpp src/*.hpp tests/*.cpp

# --- The guest: built without the QNX SDP, run by nbt-runner as its own
# process (sdk/guest). FinalBurn Neo holds LGPL code (c6280, ymf278b), which
# the QNX licence forbids linking statically with QNX code: a guest, never a
# module or a QNX build (the licence gate checks). ---
GUEST_APP := $(BUILD_DIR)/nbt-fbneo.guest
# Every licence of the linked objects (legal/README.md): FinalBurn Neo's own
# (non-commercial) and MAME's, its BSD-3-Clause and MIT files, the LGPL and
# dual-GPL files among its sound chips and CPU cores, the libraries it
# bundles, and ours.
GUEST_APP_LICENSE := LicenseRef-FBNeo AND LicenseRef-MAME AND BSD-3-Clause AND MIT \
	AND LGPL-2.1-or-later AND GPL-2.0-or-later AND Zlib AND BSD-2-Clause AND libpng-2.0 AND FTL \
	AND MIT-0 AND OFL-1.1 AND LicenseRef-uGUI AND MPL-2.0
MOD_APP_CXXFLAGS := $(NBT_MOD_CXXFLAGS) -O2 -std=c++11 -Wall -Wextra -Werror -fno-exceptions -fno-rtti \
	$(APP_INC)

$(OBJ_DIR)/guest/src/games.o: src/games.cpp $(call core_lib,guest) $(call stamp,guest) | nbt-sdk-mod
	@mkdir -p $(dir $@)
	$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS) $(call upstream_flags,guest) -MMD -MP -c $< -o $@

$(OBJ_DIR)/guest/src/%.o: src/%.cpp $(call stamp,guest) | nbt-sdk-mod
	@mkdir -p $(dir $@)
	$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS) -MMD -MP -c $< -o $@

GUEST_OBJ := $(call app_objs,guest) $(call core_lib,guest)
# Linked with its symbols (for crash addresses, with its .map), then shipped
# without them: every driver makes a large guest, and a package holds 64 MiB.
GUEST_UNSTRIPPED := $(BUILD_DIR)/unstripped/nbt-fbneo.guest

$(GUEST_UNSTRIPPED): $(GUEST_OBJ) $(NBT_SDK_MOD_DEPS)
	@mkdir -p $(dir $@)
	$(call nbt_guest_link,$@,$(GUEST_OBJ),$(GUEST_APP_LICENSE))

$(GUEST_APP): $(GUEST_UNSTRIPPED)
	$(NBT_LLVM_BIN)/llvm-strip --strip-all -o $@ $<
	$(NBT_MOD_CHECK) $@
	@size=$$(stat -c %s $@); echo "$@: $$((size / 1048576)) MiB ($$size bytes; a package holds 64 MiB)"; \
		test $$size -le 67108864 || { echo "$@ is larger than a package holds"; exit 1; }

guest: $(GUEST_APP)

# --- The guest in QNX 6.5 SP1 under QEMU (the SDK's tools/qnx65-vm; no GPU,
# no sound: both faked): a health check, then the romset of
# tests/test_fbneo.py played, which must draw frames and stop cleanly. ---
VM_GAME := $(BUILD_DIR)/vm/invaders.zip
VM_PLAY := NBT_LAUNCH=user NBT_SURFACE=5 NBT_RUNNER_FAKE_GL=1 NBT_RUNNER_FAKE_AUDIO=1 \
	NBT_DATA_DIR=/dev/shmem NBT_FILES_DIR=/proc/boot

$(VM_GAME): tests/test_fbneo.py
	@mkdir -p $(dir $@)
	python3 -c 'import sys; sys.path.insert(0, "tests"); import test_fbneo; \
		open(sys.argv[1], "wb").write(test_fbneo.romset_zip())' $@

vm-test: $(NBT_SDK_RUNNER) $(GUEST_APP) $(VM_GAME)
	QEMU_RUN_SECS=240 $(NBT_SDK_ROOT)/tools/qnx65-vm/run.sh \
		-c "NBT_LAUNCH=check NBT_DATA_DIR=/dev/shmem nbt-runner --nbt-payload /proc/boot/$(notdir $(GUEST_APP)) &" \
		-c "waitfor /none 10" -c "slay -s TERM nbt-runner" -c "waitfor /none 3" \
		-c "$(VM_PLAY) nbt-runner --nbt-payload /proc/boot/$(notdir $(GUEST_APP)) --game invaders.zip &" \
		-c "waitfor /none 60" -c "slay -s TERM nbt-runner" -c "waitfor /none 3" \
		-x 'stage: check' -x 'game invaders\.zip: ' -x 'fake-gl: closed: [1-9][0-9]* frames' \
		-x 'runner: guest exited status=0' \
		$^

# --- The signed package (release/package.args describes it) ---
PACKAGE_INPUT ?= $(GUEST_APP)
PACKAGE := $(BUILD_DIR)/fbneo-$(APP_VERSION).nbt

package: $(PACKAGE_INPUT)
	@test -f "$(APP_KEY)" || { echo "APP_KEY must name the RSA signing key"; exit 1; }
	@test -f "$(NBT_MGR_DIR)/tools/package.py" || { echo "NBT_MGR_DIR=$(NBT_MGR_DIR) has no tools/package.py"; exit 1; }
	rm -f $(PACKAGE)
	python3 $(NBT_MGR_DIR)/tools/package.py @release/package.args \
		--version "$(APP_VERSION)" \
		--sequence "$(APP_SEQ)" \
		--key "$(APP_KEY)" \
		--output $(PACKAGE) \
		$(PACKAGE_INPUT)

# legal/NOTICE.txt (tools/make_notice.py): again when the pin, a bundled
# library or the toolchain changes.
notice:
	NBT_SDK_DIR=$(NBT_SDK_ROOT) NBT_TOOLCHAIN=$(NBT_TOOLCHAIN) python3 tools/make_notice.py

clean:
	rm -rf $(BUILD_DIR)

DEPS := $(shell find $(OBJ_DIR) -name '*.d' 2>/dev/null)
-include $(DEPS)

$(call nbt_stamp,$(call stamp,host),$(CXX) $(APP_INC) $(APP_CXXFLAGS),$(CXX))
$(call nbt_stamp,$(call stamp,asan),$(CXX) $(APP_INC) $(APP_CXXFLAGS) $(ASAN_FLAGS) -fsanitize=undefined,$(CXX))
$(call nbt_stamp,$(call stamp,guest),$(NBT_MOD_CXX) $(MOD_APP_CXXFLAGS),,$(NBT_TOOLCHAIN)/VERSION)
$(call nbt_stamp,$(call stamp,core-host),$(CORE_MAKE_ARGS) $(CORE_ENV_host) $(CORE_ARGS_host),$(CC) $(CXX))
$(call nbt_stamp,$(call stamp,core-asan),$(CORE_MAKE_ARGS) $(CORE_ENV_asan) $(CORE_ARGS_asan),$(CC) $(CXX))
$(call nbt_stamp,$(call stamp,core-guest),$(CORE_MAKE_ARGS) $(CORE_ENV_guest) $(CORE_ARGS_guest),, \
	$(NBT_TOOLCHAIN)/VERSION)
