"""BaoStock provider availability probe for v0.7.1."""

from __future__ import annotations

import importlib.util
from typing import Any


def probe_baostock() -> dict[str, Any]:
    available = importlib.util.find_spec("baostock") is not None
    return {
        "provider": "baostock_provider",
        "succeeded": False,
        "available": available,
        "rows": [],
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "reason": "not used in v0.7.1 foundation run" if available else "baostock package not installed",
    }

