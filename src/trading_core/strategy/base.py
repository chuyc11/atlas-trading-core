"""Strategy protocol helpers."""

from __future__ import annotations

from typing import Any, Protocol


class Strategy(Protocol):
    strategy_id: str

    def generate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        ...
