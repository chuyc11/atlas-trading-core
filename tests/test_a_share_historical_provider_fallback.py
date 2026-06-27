from __future__ import annotations

from a_share_historical_test_utils import fake_price_provider_result
from trading_core.integrations.public_data import historical_provider_fallback as fallback


def test_provider_fallback_records_failure_then_success(monkeypatch) -> None:
    def eastmoney(symbols, **kwargs):
        return {
            "provider": "eastmoney_kline_public_http",
            "attempted_symbols": symbols,
            "succeeded_symbols": [],
            "failed_symbols": [{"symbol": symbol, "reason": "rate limited"} for symbol in symbols],
            "symbol_results": [
                {
                    "symbol": symbol,
                    "provider": "eastmoney_kline_public_http",
                    "provider_attempted": True,
                    "provider_succeeded": False,
                    "provider_failed": True,
                    "row_count": 0,
                    "failure_reason": "rate limited",
                }
                for symbol in symbols
            ],
            "rows": [],
            "external_api_called": True,
        }

    def akshare(symbols, **kwargs):
        return fake_price_provider_result(symbols=symbols, periods=260) | {
            "provider": "akshare_provider",
            "providers_attempted": ["akshare_provider"],
            "providers_succeeded": ["akshare_provider"],
            "symbol_results": [
                {
                    "symbol": symbol,
                    "provider": "akshare_provider",
                    "provider_attempted": True,
                    "provider_succeeded": True,
                    "provider_failed": False,
                    "row_count": 260,
                    "failure_reason": "",
                }
                for symbol in symbols
            ],
        }

    monkeypatch.setattr(fallback, "fetch_eastmoney_price_history", eastmoney)
    monkeypatch.setattr(fallback, "fetch_akshare_price_history", akshare)

    result = fallback.fetch_price_history_with_fallback(
        ["600000.SH"],
        start_date="2023-01-01",
        end_date="2026-06-26",
        provider_priority=["eastmoney", "akshare"],
    )

    assert result["providers_attempted"] == ["eastmoney_kline_public_http", "akshare_provider"]
    assert result["providers_succeeded"] == ["akshare_provider"]
    assert result["provider_breakdown"]["eastmoney_kline_public_http"]["failed_symbol_count"] == 1
    assert result["provider_breakdown"]["akshare_provider"]["succeeded_symbol_count"] == 1
