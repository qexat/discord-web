#!/usr/bin/env python

from __future__ import annotations

import argparse
import enum
import os
import stat
import subprocess
import sys
import textwrap
from typing import Literal

import alloy

HOME = os.environ["HOME"]
BIN_PATH = os.path.join(HOME, ".local/bin/")
DATA_PATH = os.environ.get(
    "XDG_DATA_HOME",
    os.path.join(HOME, ".local/share/"),
)
DESKTOP_DATA_PATH = os.path.join(DATA_PATH, "applications")

RELEASE_CHANNEL_ARG = "--chrome-release-channel"

LAUNCHING_SCRIPT_TEMPLATE = """\
#!/bin/bash

google-chrome-{} --app="https://app.discord.com/" --disable-infobars --disable-logging --start-maximized >/dev/null 2>&1 & 
"""

# TODO: use custom icon to distinguish with normal app
DESKTOP_ENTRY = """\
[Desktop Entry]
Name=Discord Web
Exec=discord-web
Icon=discord
Type=Application
Terminal=false
"""


class Program:
    def __init__(
        self,
        *,
        chrome_release_channel: alloy.ReleaseChannel | Literal["auto"],
        debug: bool,
        dry_run: bool,
    ) -> None:
        self.chosen_channel = alloy.ReleaseChannel.parse(chrome_release_channel)
        self.debug = True if dry_run else debug
        self.dry_run = dry_run

    @staticmethod
    def from_parsing_args() -> Program:
        parser = argparse.ArgumentParser()

        _ = parser.add_argument(
            RELEASE_CHANNEL_ARG,
            "-c",
            choices=(*alloy.ReleaseChannel, "auto"),
            default="auto",
            help="specify which Chrome release channel to use\n 'auto' "
            "will search for the most stable release installed on your "
            "system",
        )

        _ = parser.add_argument(
            "--debug",
            action="store_true",
            help="this program will describe what it is doing at each step",
        )
        _ = parser.add_argument(
            "--dry-run",
            action="store_true",
            help="this program will not perform any action ; implies --debug",
        )

        return Program(**vars(parser.parse_args()))

    def print_error(self, message: str, *hints: str) -> None:
        print(f"\x1b[1;31mERROR:\x1b[22;39m {message}", file=sys.stderr)

        if hints:
            for hint in hints:
                print(
                    f"\x1b[1;34mHINT:\x1b[22;39m {hint}",
                    file=sys.stderr,
                )

    def print_debug(self, *lines: str) -> None:
        if self.debug:
            for line in lines:
                print(
                    f"\x1b[1;35mDEBUG:\x1b[22;39m {line}",
                    file=sys.stderr,
                )

    def print_file(self, path: str, contents: str) -> None:
        self.print_debug(
            f"\x1b[32m{path}\x1b[39m:",
            *(textwrap.indent(contents, "    ").splitlines()),
        )

    def write_file(self, path: str, contents: str) -> None:
        if self.debug:
            self.print_file(path, contents)

        if not self.dry_run:
            with open(path, "w", encoding="utf-8") as file:
                _ = file.write(contents)

    def run(self) -> int:
        # --chrome-release-channel=auto
        if self.chosen_channel is None:
            installed_channels = alloy.ReleaseChannel.collect_installed()
            channel = alloy.select_most_stable_release_channel(installed_channels)

            if channel is None:
                self.print_error("Chrome is not installed on your system or is not on PATH.")
        else:
            if not alloy.ReleaseChannel(self.chosen_channel).is_installed():
                self.print_error(
                    f"Release channel {self.chosen_channel} is "
                    "not installed on your system.",
                    f"try using {RELEASE_CHANNEL_ARG}='auto'",
                )

                return os.EX_UNAVAILABLE

            channel = self.chosen_channel

        self.print_debug(f"release channel is {channel}")

        launching_path = os.path.join(BIN_PATH, "discord-web")

        self.write_file(
            launching_path,
            LAUNCHING_SCRIPT_TEMPLATE.format(channel),
        )

        file_stat = os.stat(launching_path)
        os.chmod(launching_path, file_stat.st_mode | stat.S_IEXEC)

        self.write_file(
            os.path.join(DESKTOP_DATA_PATH, "Discord Web.desktop"),
            DESKTOP_ENTRY,
        )

        print(
            f"\x1b[1;32mSUCCESS:\x1b[22;39m Discord Web "
            f"(google-chrome-{channel}) was installed."
        )

        return os.EX_OK


def main() -> int:
    """
    Entry point.
    """

    return Program.from_parsing_args().run()


if __name__ == "__main__":
    raise SystemExit(main())
