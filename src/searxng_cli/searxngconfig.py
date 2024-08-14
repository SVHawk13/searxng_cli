from typing import Any

from searxng_cli.outputformat import OutputFormat

DEFAULT_BASE_URL = "http://localhost"


class SearxngConfig:
    __slots__ = ("_base_url", "_output_format", "_timeout", "_verify_ssl")

    def __init__(
        self,
        base_url: str | None = None,
        output_format: OutputFormat | str = OutputFormat.JSON,
        timeout: float | int = 30.0,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url or DEFAULT_BASE_URL
        self.output_format = OutputFormat.from_value(output_format)
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        if not isinstance(base_url, str):
            raise TypeError
        self._base_url = base_url

    @property
    def output_format(self) -> str:
        return str(self.output_format)

    @output_format.setter
    def output_format(self, output_format: OutputFormat | str) -> None:
        if not isinstance(output_format, (OutputFormat, str)):
            raise TypeError
        self._output_format = OutputFormat.from_value(output_format)

    @property
    def timeout(self) -> float:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float | int) -> None:
        _timeout = float(timeout)
        if _timeout < 0.0:
            msg = "timeout must not be negative."
            raise ValueError(msg)
        self._timeout = _timeout

    @property
    def verify_ssl(self) -> bool:
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, verify_ssl: bool) -> None:
        if verify_ssl is True or verify_ssl is False:
            self._verify_ssl = verify_ssl
            return
        raise TypeError

    def asdict(self) -> dict[str, Any]:
        return {
            "base_url": self.base_url,
            "output_format": OutputFormat.from_value(self.output_format),
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
        }
