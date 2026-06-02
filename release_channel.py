"""
Small library to deal with Chrome release channels and check which ones
are installed.

The list used is based on the one provided here:
<https://www.chromium.org/getting-involved/chrome-release-channels/>
"""

import enum
import subprocess
from collections.abc import Iterable
from collections.abc import Sequence
from typing import final

import dry_mode

@final
class ReleaseChannel(enum.StrEnum):
    """
    Chrome release channel option.
    """

    STABLE = enum.auto()
    BETA = enum.auto()
    DEV = enum.auto()
    CANARY = enum.auto()

    def __repr__(self) -> str:
        return repr(self.name.lower())

def try_parse_channel_name(string: str) -> ReleaseChannel | None:
    """
    Return the release channel associated with the name in the string if
    there is one, otherwise return None.
    """

    return ReleaseChannel(string) if string in ReleaseChannel else None

def collect_installed(
    *,
    assume_uninstalled: Sequence[ReleaseChannel] = (),
) -> Iterable[ReleaseChannel]:
    """
    Collect every Chrome release channel installed on the machine.
    """

    for channel in ReleaseChannel:
        if channel in assume_uninstalled:
            continue

        process = subprocess.run(
            f"command -v google-chrome-{channel}",
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )

        if process.returncode == 0:
            yield channel

@dry_mode.make_dryable(default_return_value=True)
def is_channel_installed(channel: ReleaseChannel) -> bool:
    """
    Return whether the given channel is installed on the machine or not.
    """

    return channel in collect_installed()

def get_unstability_level(channel: ReleaseChannel) -> int:
    """
    Produce an integer that determines how unstable the release channel is,
    where 0 is the most stable one.
    """

    match channel:
        case ReleaseChannel.STABLE:
            return 0
        case ReleaseChannel.BETA:
            return 1
        case ReleaseChannel.DEV:
            return 2
        case ReleaseChannel.CANARY:
            return 3

def select_most_stable(
    channels: Sequence[ReleaseChannel],
) -> ReleaseChannel | None:
    """
    Return the most stable release channel given a list of channels.
    If the list is empty, return None.
    """

    if not channels:
        return None

    return min(channels, key=get_unstability_level)

STABLE = ReleaseChannel.STABLE
BETA = ReleaseChannel.BETA
DEV = ReleaseChannel.DEV
CANARY = ReleaseChannel.CANARY
