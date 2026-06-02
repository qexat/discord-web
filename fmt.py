from __future__ import annotations

import enum
import io
import sys
from typing import Literal

import global_switch

_DEBUG_MODE = global_switch.GlobalSwitch()

def set_debug_mode(enabled_or_disabled: bool) -> None:
    _DEBUG_MODE.set(enabled_or_disabled)

type LogType = Literal["success", "warning", "error", "info", "debug", "hint"]

class Color(enum.IntEnum):
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6

def format_log(type: LogType, color: Color, message: str) -> str:
    return f"\x1b[1;3{color}m{type}:\x1b[22;39m {message}\n"

def format_success(message: str) -> str:
    return format_log("success", Color.GREEN, message)

def format_warning(message: str) -> str:
    return format_log("warning", Color.YELLOW, message)

def format_error(message: str, *hints: str) -> str:
    return "".join(
        (
            format_log("error", Color.RED, message),
            *(format_log("hint", Color.BLUE, hint) for hint in hints),
        )
    )

def format_info(message: str) -> str:
    return format_log("info", Color.BLUE, message)

def format_debug(*lines: str) -> str:
    return "".join(format_log("debug", Color.MAGENTA, line) for line in lines)

def output_formatted_success(message: str) -> None:
    sys.stderr.write(format_success(message))

def output_formatted_warning(message: str) -> None:
    sys.stderr.write(format_warning(message))

def output_formatted_error(message: str, *hints: str) -> None:
    sys.stderr.write(format_error(message, *hints))

def output_formatted_info(message: str) -> None:
    sys.stderr.write(format_info(message))

def output_formatted_debug(*lines: str) -> None:
    if _DEBUG_MODE:
        sys.stderr.write(format_debug(*lines))
