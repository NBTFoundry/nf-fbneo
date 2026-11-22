#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Keeps the FinalBurn Neo version in release/package.args equal to the pin's:
the phone app shows it before an install (NBT Manager's PROTOCOL.md, "Package
information"). It is the pinned src/burn/version.h's, with the pinned commit
(FinalBurn Neo publishes no releases). `make package-args` writes it; with
--check (`make test`), fails when the file lags the pin.

    package_version.py [--check] release/package.args
"""
import re
import subprocess
import sys

LABEL = "FinalBurn Neo"
UPSTREAM = "third_party/fbneo"


def pinned():
    path = UPSTREAM + "/src/burn/version.h"
    with open(path) as f:
        text = f.read()
    parts = [re.search(r"^#define VER_%s\s+(\d+)\s*$" % name, text, re.M)
             for name in ("MAJOR", "MINOR", "BETA", "ALPHA")]
    if not all(parts):
        sys.exit("%s: no VER_MAJOR, VER_MINOR, VER_BETA and VER_ALPHA" % path)
    commit = subprocess.run(["git", "-C", UPSTREAM, "rev-parse", "--short=7", "HEAD"],
                            check=True, capture_output=True, text=True).stdout.strip()
    # As FinalBurn Neo writes it: 1.0.0.03.
    major, minor, beta, alpha = (int(part.group(1)) for part in parts)
    return "%d.%d.%d.%02d (%s)" % (major, minor, beta, alpha, commit)


def main():
    args = sys.argv[1:]
    check = args[:1] == ["--check"]
    args = args[1:] if check else args
    if len(args) != 1:
        sys.exit(__doc__)
    path = args[0]
    with open(path) as f:
        lines = f.read().split("\n")
    at = [i + 1 for i in range(len(lines) - 1)
          if lines[i] == "--property" and lines[i + 1].startswith(LABEL + "|")]
    if len(at) != 1:
        sys.exit("%s: needs one --property %s|<version>" % (path, LABEL))
    want = "%s|%s" % (LABEL, pinned())
    if lines[at[0]] == want:
        return
    if check:
        sys.exit("%s: %s, the pin builds %s: make package-args" % (path, lines[at[0]], want))
    lines[at[0]] = want
    with open(path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
