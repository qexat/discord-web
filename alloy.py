"""
Alloy is a small library to deal with Chrome release channels
and check which ones are installed.

The list used is based on the one provided here:
<https://www.chromium.org/getting-involved/chrome-release-channels/>
"""

import enum
import subprocess
from collections.abc import Iterable
from typing import final

@final
class ReleaseChannel(enum.StrEnum):
    """
    Chrome release channel option.
    """

    STABLE = enum.auto()
    BETA = enum.auto()
    DEV = enum.auto()
    CANARY = enum.auto()

    def is_installed(self) -> bool:
        return self in ReleaseChannel.collect_installed()

    def get_unstability_level(self) -> int:
        """
        Produce an integer that determines how unstable the release channel is,
        where 0 is the most stable one.
        """

        match self:
            case ReleaseChannel.STABLE:
                return 0
            case ReleaseChannel.BETA:
                return 1
            case ReleaseChannel.DEV:
                return 2
            case ReleaseChannel.CANARY:
                return 3

    @classmethod
    def parse(cls, name: str) -> ReleaseChannel | None:
        return cls(name) if name in cls else None

    @classmethod
    def collect_installed(cls) -> Iterable[ReleaseChannel]:
        """
        Collect every Chrome release channel installed on the machine.
        """

        for channel in cls:
            process = subprocess.run(
                f"command -v google-chrome-{channel}",
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )

            if process.returncode == 0:
                yield channel


def select_most_stable_release_channel(
    channels: Iterable[ReleaseChannel],
) -> ReleaseChannel | None:
    if not channels:
        return None

    first, *rest = channels
    current = first

    for channel in rest:
        if channel.get_unstability_level() < current.get_unstability_level():
            current = channel

    return current
