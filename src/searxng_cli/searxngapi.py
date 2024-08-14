from dataclasses import dataclass, field
from typing import Any

import requests

from searxng_cli.endpoint import Endpoint
from searxng_cli.outputformat import OutputFormat
from searxng_cli.pluginstatus import PluginStatus
from searxng_cli.searchresult import SearchResult
from searxng_cli.searxngconfig import SearxngConfig


@dataclass
class SearxngApi:
    config: SearxngConfig = field(default_factory=SearxngConfig())

    @property
    def endpoints(self) -> list[str]:
        return Endpoint.list_valid()

    @property
    def timeout(self) -> float | int:
        return self.config.timeout

    @timeout.setter
    def timeout(self, _timeout: float | int, /) -> None:
        if not isinstance(_timeout, (float, int)):
            raise TypeError
        elif _timeout < 0:
            msg = "timeout must be non-negative."
            raise ValueError(msg)
        self.config.timeout = _timeout

    def _get_format(self, _format, /) -> OutputFormat:
        if isinstance(_format, OutputFormat):
            return _format
        try:
            format = OutputFormat.from_value(_format)
        except ValueError:
            format = None
        except TypeError:
            format = None
        return format or self.config.output_format

    def _get_verify_ssl(self, _verify_ssl):
        if (_verify_ssl is True) or (_verify_ssl is False):
            return _verify_ssl
        return self.config.verify_ssl

    def _get_timeout(self, _timeout, /) -> OutputFormat:
        if not isinstance(_timeout, (float, int)):
            return self.timeout
        if _timeout < 0:
            return self.timeout
        return _timeout

    @staticmethod
    def _parse_search_result(
        __search_result: dict[str, Any], asjson: bool = False
    ) -> list[SearchResult] | list[dict[str, Any]]:
        results = []
        for raw_result in __search_result["results"]:
            search_result = SearchResult.from_dict(raw_result)
            results.append(search_result)
        results.sort(key=lambda x: x.score)
        result_count = len(results)
        final_result = {
            "query": __search_result["query"],
            "number_of_results": result_count,
            "results": [result.asjson() for result in results] if asjson else results,
            "unresponsive_engines": __search_result["unresponsive_engines"],
        }
        return final_result

    def format_url(self, endpoint: Endpoint | str, base_url: str) -> str:
        if isinstance(endpoint, str):
            endpoint = Endpoint(endpoint.lower())
        return endpoint.resolve(base_url or self.config.base_url)

    def get_server_config(
        self,
        format: OutputFormat | str | None = None,
        verify_ssl: bool = False,
        timeout: float | int | None = None,
    ) -> dict | list:
        url = Endpoint.CONFIG.resolve(self.config.base_url)
        format = self._get_format(format)
        verify_ssl = self._get_verify_ssl(verify_ssl)
        timeout = self._get_timeout(timeout)
        req_data = {"format": format.value}
        with requests.get(
            url=url, data=req_data, verify=verify_ssl, timeout=timeout
        ) as response:
            response.raise_for_status()
            result = response.json()
            assert isinstance(result, (dict, list))
        return result

    def get_server_plugins(
        self, *args, status: str | PluginStatus = PluginStatus.ALL, **kwargs
    ) -> dict[str, list[str]] | list[str]:
        status = PluginStatus.from_value(status)
        config = self.get_server_config(*args, **kwargs)
        plugins = config["plugins"]
        result = {}
        if status & PluginStatus.DISABLED:
            result["disabled"] = [p["name"] for p in plugins if p["enabled"] is False]
        if status & PluginStatus.ENABLED:
            result["enabled"] = [p["name"] for p in plugins if p["enabled"] is True]

        if status is PluginStatus.ALL:
            return result
        else:
            return result[status.name.lower()]

    def get_server_categories(self, *args, **kwargs) -> list[str]:
        config = self.get_server_config(*args, **kwargs)
        return config["categories"]

    def check_categories(
        self, categories, valid_categories: set[str] | frozenset[str] | None
    ) -> None:
        if not categories:
            return
        if not isinstance(valid_categories, (set, frozenset)):
            _valid_categories = frozenset(self.get_server_categories())
        category_set = frozenset(categories)
        if not _valid_categories.issuperset(category_set):
            invalid = category_set.difference(_valid_categories)
            msg = f"The following categories are invalid: {', '.join(sorted(invalid))}"
            raise ValueError(msg)
        return

    def get_server_error_stats(
        self,
        format: OutputFormat | str | None = None,
        verify_ssl: bool = False,
        timeout: float | int | None = None,
    ) -> dict | list:
        url = Endpoint.ERROR_STATS.resolve(self.config.base_url)
        format = self._get_format(format)
        timeout = self._get_timeout(timeout)
        verify_ssl = self._get_verify_ssl(verify_ssl)
        req_data = {"format": format.value}
        data = {k: v for (k, v) in req_data.items() if v is not None}
        with requests.get(
            url=url, data=data, verify=verify_ssl, timeout=timeout
        ) as response:
            response.raise_for_status()
            result = response.json()
            assert isinstance(result, (dict, list))
        return result

    def search(
        self,
        query: str,
        categories: list[str] | None = None,
        engines: list[str] | None = None,
        format: OutputFormat | str | None = None,
        verify_ssl: bool = False,
        timeout: float | int | None = None,
    ) -> dict | list:
        url = Endpoint.SEARCH.resolve(self.config.base_url)
        format = self._get_format(format)
        timeout = self._get_timeout(timeout)
        verify_ssl = self._get_verify_ssl(verify_ssl)
        if categories:
            valid_categories = {
                c.replace(" ", "_")
                for c in self.get_server_categories(
                    format=format, verify_ssl=verify_ssl, timeout=timeout
                )
            }
            self.check_categories(
                categories=categories, valid_categories=valid_categories
            )
        req_data = {
            "q": query,
            "format": format.value,
            "categories": categories,
            "engines": engines,
        }
        data = {k: v for (k, v) in req_data.items() if v is not None}
        print(url)
        print(f"base url: {self.config.base_url}")
        with requests.post(
            url=url, data=data, verify=verify_ssl, timeout=timeout
        ) as response:
            response.raise_for_status()
            result = response.json()
            assert isinstance(result, (dict, list))
        result = self._parse_search_result(result, asjson=True)
        return result
