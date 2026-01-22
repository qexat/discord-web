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


class ReleaseChannel(enum.StrEnum):
    """
    Chrome release channel option.
    """

    STABLE = enum.auto()
    BETA = enum.auto()
    DEV = enum.auto()
    CANARY = enum.auto()


class Program:
    def __init__(
        self,
        *,
        chrome_release_channel: ReleaseChannel | Literal["auto"],
        debug: bool,
        dry_run: bool,
    ) -> None:
        self.release_channel: ReleaseChannel | Literal["auto"] = (
            chrome_release_channel
        )
        self.debug = True if dry_run else debug
        self.dry_run = dry_run

    @staticmethod
    def from_parsing_args() -> Program:
        parser = argparse.ArgumentParser()

        _ = parser.add_argument(
            RELEASE_CHANNEL_ARG,
            "-c",
            choices=(*ReleaseChannel, "auto"),
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

        return Program(**parser.parse_args().__dict__)

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

    def check_release_channel(self, channel: ReleaseChannel) -> bool:
        """
        Check if the release channel is installed on the system.
        """

        shell_command = f"command -v google-chrome-{channel}"
        self.print_debug(f"checking channel: {shell_command}")

        process = subprocess.run(  # noqa: S602
            shell_command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )

        if self.debug:
            self.print_debug(
                f"command output:",
                *(textwrap.indent(process.stdout, "    ").splitlines()),
            )

        return process.returncode == 0

    def determine_release_channel(self) -> ReleaseChannel | None:
        """
        Look for the release channel installed on the system.

        If Google Chrome is not installed, returns None.

        If several channels are installed, the most stable one is
        picked, based on the list provided here:
        https://www.chromium.org/getting-involved/chrome-release-channels/
        """

        if self.dry_run:
            self.print_debug("dry: pretending channel stable is installed")

            return ReleaseChannel.STABLE

        for channel in ReleaseChannel:
            if self.check_release_channel(channel):
                self.print_debug(f"channel {channel} is installed")

                return channel

        self.print_debug("no channel was found to be installed")

        return None

    def write_file(self, path: str, contents: str) -> None:
        if self.debug:
            self.print_file(path, contents)

        if not self.dry_run:
            with open(path, "w", encoding="utf-8") as file:
                _ = file.write(contents)

    def run(self) -> int:
        match self.release_channel:
            case "auto":
                self.print_debug("release channel is set to 'auto'")
                self.print_debug(
                    "determining which channel is installed..."
                )

                release_channel = self.determine_release_channel()
            case _:
                if not self.check_release_channel(self.release_channel):
                    self.print_error(
                        f"The release channel {self.release_channel} does "
                        "not seem to be installed on your system.",
                        f"try using {RELEASE_CHANNEL_ARG}='auto'",
                    )

                    return os.EX_UNAVAILABLE

                release_channel = self.release_channel

        if release_channel is None:
            self.print_error(
                "Chrome does not seem to be installed on your system.",
                "maybe it is installed, but not on PATH?",
            )

            return os.EX_UNAVAILABLE

        self.print_debug(f"release channel is {release_channel}")

        launching_path = os.path.join(BIN_PATH, "discord-web")

        self.write_file(
            launching_path,
            LAUNCHING_SCRIPT_TEMPLATE.format(release_channel),
        )

        file_stat = os.stat(launching_path)
        os.chmod(launching_path, file_stat.st_mode | stat.S_IEXEC)

        self.write_file(
            os.path.join(DESKTOP_DATA_PATH, "Discord Web.desktop"),
            DESKTOP_ENTRY,
        )

        print(
            f"\x1b[1;32mSUCCESS:\x1b[22;39m Discord Web "
            f"(google-chrome-{release_channel}) was installed."
        )

        return os.EX_OK


def main() -> int:
    """
    Entry point.
    """

    return Program.from_parsing_args().run()


if __name__ == "__main__":
    raise SystemExit(main())
