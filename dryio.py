"""
Wrapper around basic I/O functions to make them not execute if dry-mode is
enabled.
"""

from __future__ import annotations

import os
import stat

import dry_mode

@dry_mode.make_dryable()
def write_file(path: str, contents: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        _ = file.write(contents)

@dry_mode.make_dryable()
def make_file_executable(path: str) -> None:
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)

@dry_mode.make_dryable(default_return_value=True)
def does_file_exist(path: str) -> bool:
    return os.path.exists(path)
