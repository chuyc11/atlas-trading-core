from __future__ import annotations

from trading_core.cli import build_parser


def test_full_market_cli_default_max_symbols_is_unlimited() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "backfill-a-share-historical-panels-full-market",
            "--target-start-date",
            "2021-01-01",
            "--minimum-start-date",
            "2023-01-01",
            "--end-date",
            "2026-06-26",
        ]
    )

    assert args.max_symbols == 0
    assert args.sample_size is None


def test_daily_price_history_cli_default_max_symbols_is_unlimited() -> None:
    parser = build_parser()
    args = parser.parse_args(["backfill-a-share-daily-price-history", "--start-date", "2021-01-01", "--end-date", "2026-06-26"])

    assert args.max_symbols == 0
