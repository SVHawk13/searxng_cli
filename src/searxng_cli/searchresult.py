from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any


@dataclass(slots=True, kw_only=True)
class SearchResult:
    url: str
    page_title: str
    summary: str
    engine: list[str]
    parsed_url: list[str]
    template: str
    positions: list[int]
    score: Decimal
    category: list[str]

    @staticmethod
    def _ensure_list(__val) -> list:
        if isinstance(__val, list):
            return __val
        else:
            return [__val]

    @classmethod
    def from_dict(cls, search_result: dict[str, Any]):
        return cls(
            url=search_result["url"],
            page_title=search_result["title"],
            summary=search_result["content"],
            engine=cls._ensure_list(search_result["engine"]),
            parsed_url=cls._ensure_list(search_result["parsed_url"]),
            template=search_result["template"],
            positions=cls._ensure_list(search_result["positions"]),
            score=Decimal(search_result["score"]),
            category=cls._ensure_list(search_result["category"]),
        )

    def asdict(self) -> dict[str, Any]:
        return asdict(self)

    def asjson(self) -> dict[str, Any]:
        _d = asdict(self)
        return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in _d.items()}
