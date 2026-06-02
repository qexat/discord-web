#!/usr/bin/env python

from __future__ import annotations

import argparse
import os
import sys
from typing import Literal

import default
import dryio
import dry_mode
import fmt
import release_channel

HOME = os.environ["HOME"]
BIN_PATH = os.path.join(HOME, ".local/bin/")
DATA_PATH = os.environ.get(
    "XDG_DATA_HOME",
    os.path.join(HOME, ".local/share/"),
)
DESKTOP_DATA_PATH = os.path.join(DATA_PATH, "applications")
ICONS_PATH = os.path.join(DATA_PATH, "icons")

TEMPLATE_LAUNCHING_SCRIPT = """\
#!/bin/bash

google-chrome-{} --app="https://app.discord.com/" --disable-infobars --disable-logging --start-maximized >/dev/null 2>&1 & 
"""

# TODO: use custom icon to distinguish with normal app
DESKTOP_ENTRY_CONTENTS = """\
[Desktop Entry]
Name=Discord Web
Exec=discord-web
Icon=discord
Type=Application
Terminal=false
"""

def select_release_channel(
    chosen_channel: release_channel.ReleaseChannel | Literal["auto"],
    channels_assume_uninstalled: list[release_channel.ReleaseChannel],
) -> release_channel.ReleaseChannel | None:
    if chosen_channel == "auto":
        installed_channels = release_channel.collect_installed(
            assume_uninstalled=channels_assume_uninstalled,
        )

        channel = release_channel.select_most_stable(
            list(installed_channels),
        )

        if channel is None:
            fmt.output_formatted_error(
                "Chrome is not installed on your system.",
                "maybe it is installed, but not on PATH?"
            )
            return None

        return channel
    else:
        if not release_channel.is_channel_installed(chosen_channel):
            fmt.output_formatted_error(
                f"release channel {chosen_channel!r} is not "
                f"installed on your system.",
                f"try using --chrome-release-channel='auto'",
            )
            return None

        return chosen_channel

def main(
    chosen_channel: release_channel.ReleaseChannel | Literal["auto"],
    channels_assume_uninstalled: list[release_channel.ReleaseChannel],
    in_debug_mode: bool,
    in_dry_mode: bool,
) -> int:
    """
    Entry point of the program.
    """

    fmt.set_debug_mode(in_debug_mode)
    dry_mode.set(in_dry_mode)

    if dry_mode.IS_ENABLED:
        fmt.output_formatted_info(
            "dry-mode enabled, side effects won't be performed",
        )

    if not dryio.does_file_exist(os.path.join(ICONS_PATH, "discord")):
        fmt.output_formatted_warning(f"icon was not found")

    channel = select_release_channel(
        chosen_channel,
        channels_assume_uninstalled,
    )

    if channel is None:
        return os.EX_UNAVAILABLE

    fmt.output_formatted_debug(f"selected release channel {channel!r}")

    launching_script_path = os.path.join(BIN_PATH, "discord-web")

    dryio.write_file(
        launching_script_path,
        TEMPLATE_LAUNCHING_SCRIPT.format(channel),
    )

    dryio.make_file_executable(launching_script_path)

    dryio.write_file(
        os.path.join(DESKTOP_DATA_PATH, "Discord Web.desktop"),
        DESKTOP_ENTRY_CONTENTS,
    )

    fmt.output_formatted_success(
        f"Discord Web (google-chrome-{channel}) was installed."
    )

    return os.EX_OK

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    _ = parser.add_argument(
        f"--chrome-release-channel",
        choices=(*release_channel.ReleaseChannel, "auto"),
        default=default.CHROME_RELEASE_CHANNEL,
        help="specify which Chrome release channel to use\n 'auto' "
        "will search for the most stable release installed on your "
        "system",
        dest="chosen_channel",
    )

    _ = parser.add_argument(
        f"--chrome-channels-assume-uninstalled",
        nargs="*",
        choices=release_channel.ReleaseChannel,
        default=(),
        help="list Chrome release channels to be assumed uninstalled",
        dest="channels_assume_uninstalled",
    )

    _ = parser.add_argument(
        f"--debug",
        action="store_true",
        help="this program will describe what it is doing at each step",
        dest="in_debug_mode",
    )

    _ = parser.add_argument(
        f"--dry-run",
        action="store_true",
        help="this program will not perform any side-effect ; implies --debug",
        dest="in_dry_mode",
    )

    raise SystemExit(main(**vars(parser.parse_args())))
