import enum


class PluginStatus(enum.Flag):
    ENABLED = enum.auto()
    DISABLED = enum.auto()
    ALL = ENABLED | DISABLED

    @classmethod
    def list_valid(cls) -> list[str]:
        return sorted(member.name for member in cls.__members__.values())

    @classmethod
    def from_value(cls, _v, /) -> "PluginStatus":
        if isinstance(_v, type(cls)):
            return _v
        if isinstance(_v, str):
            _v = _v.upper()
            if _v in cls.list_valid():
                return cls[_v]
            msg = f"Invalid status: {_v}"
            raise ValueError(msg)
        elif isinstance(_v, int):
            if _v in {member.value for member in cls.__members__.values()}:
                return cls(_v)
            msg = f"Invalid status: {_v}"
            raise ValueError(msg)
        given = type(_v).__name__
        msg = f"'PluginStatus', 'str', or 'int' required, but '{given} given.'"
        raise TypeError(msg)
