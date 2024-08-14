import enum


class Endpoint(enum.StrEnum):
    SEARCH = "/search"
    CONFIG = "/config"
    ERROR_STATS = "/stats/errors"

    @classmethod
    def list_valid(cls) -> list[str]:
        return sorted(str(member) for member in cls.__members__.values())

    @classmethod
    def from_value(cls, _v, /) -> "Endpoint":
        if isinstance(_v, type(cls)):
            return _v
        valid = cls.list_valid()
        if isinstance(_v, str):
            _v = _v.lower()
            if _v in valid:
                return cls(_v)
            _v = _v.upper()
            if _v in cls.__members__.keys():
                return cls[_v]
            msg = f"Invalid endpoint: {_v}"
            raise ValueError(msg)
        msg = f"'Endpoint' or 'str' required, but '{type(_v).__name__} given.'"
        raise TypeError(msg)

    def resolve(self, base_url: str) -> str:
        return base_url.removesuffix("/") + self.value
