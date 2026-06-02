class GlobalSwitch:
    def __init__(self, *, default: bool = False) -> None:
        self.__enabled = default

    def __bool__(self) -> bool:
        return self.__enabled

    def __repr__(self) -> str:
        return f"<Global switch: {'enabled' if self.__enabled else 'disabled'}>"

    def get(self) -> bool:
        return self.__enabled

    def set(self, enabled_or_disabled: bool) -> None:
        self.__enabled = enabled_or_disabled
