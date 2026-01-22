#!/usr/bin/env python

import os
from contextlib import suppress

HOME = os.environ["HOME"]
BIN_PATH = os.path.join(HOME, ".local/bin/")
DATA_PATH = os.environ.get(
    "XDG_DATA_HOME",
    os.path.join(HOME, ".local/share/"),
)
DESKTOP_DATA_PATH = os.path.join(DATA_PATH, "applications")


def main() -> None:
    with suppress(OSError):
        os.unlink(os.path.join(BIN_PATH, "discord-web"))

    with suppress(OSError):
        os.unlink(os.path.join(DESKTOP_DATA_PATH, "Discord Web.desktop"))

    print("\x1b[1;32mSUCCESS:\x1b[22;39m Discord Web was uninstalled.")


if __name__ == "__main__":
    main()
