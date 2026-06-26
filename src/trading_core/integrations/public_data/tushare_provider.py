"""Tushare provider availability probe for v0.7.1."""

from __future__ import annotations

import importlib.util
import os
from typing import Any


def probe_tushare() -> dict[str, Any]:
    available = importlib.util.find_spec("tushare") is not None
    token_available = bool(os.environ.get("TUSHARE_TOKEN"))
    return {
        "provider": "tushare_provider",
        "succeeded": False,
        "available": available,
        "token_available": token_available,
        "rows": [],
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "reason": "not used in v0.7.1 foundation run" if available and token_available else "tushare package or token unavailable",
    }

