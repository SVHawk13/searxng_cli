import enum


class OutputFormat(enum.StrEnum):
    JSON = "json"
    CSV = "csv"
    RSS = "rss"

    @classmethod
    def list_valid(cls) -> list[str]:
        return sorted(str(member) for member in cls.__members__.values())

    @classmethod
    def from_value(cls, _v, /) -> "OutputFormat":
        if isinstance(_v, type(cls)):
            return _v
        valid = cls.list_valid()
        if isinstance(_v, str):
            _v = _v.lower()
            if _v in valid:
                return cls(_v)
            msg = f"Invalid endpoint: {_v}"
            raise ValueError(msg)
        msg = f"'OutputFormat' or 'str' required, but '{type(_v).__name__} given.'"
        raise TypeError(msg)
