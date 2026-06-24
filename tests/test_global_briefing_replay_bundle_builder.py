from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, fixture_path, make_paths, write_text
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle


def _build(paths, *, allow_carry_forward: bool = False):
    return build_global_briefing_replay_bundle(
        fixture_path(paths, "signals_valid.jsonl"),
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        allow_carry_forward=allow_carry_forward,
        paths=paths,
    )


def test_valid_signal_and_price_dates_generate_bundle(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = _build(paths)

    assert Path(result["json_path"]).exists()
    assert result["coverage"]["replay_days"] == 5


def test_future_signal_is_not_used(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = build_global_briefing_replay_bundle(
        fixture_path(paths, "signals_future.jsonl"),
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-03",
        end_date="2024-01-03",
        paths=paths,
    )

    assert result["rows"][0]["selected_signal_generated_at"] is None
    assert result["point_in_time"]["future_signal_used"] is False


def test_missing_signal_day_recorded(tmp_path: Path) -> None:
    result = _build(make_paths(tmp_path))

    assert "2024-01-04" in result["coverage"]["missing_signal_days"]


def test_carry_forward_disabled_leaves_missing(tmp_path: Path) -> None:
    result = _build(make_paths(tmp_path), allow_carry_forward=False)

    row = next(item for item in result["rows"] if item["replay_date"] == "2024-01-04")
    assert row["selected_signal_generated_at"] is None


def test_carry_forward_enabled_uses_past_signal(tmp_path: Path) -> None:
    result = _build(make_paths(tmp_path), allow_carry_forward=True)

    row = next(item for item in result["rows"] if item["replay_date"] == "2024-01-04")
    assert row["selected_signal_as_of_date"] == "2024-01-03"
    assert row["carry_forward_days"] == 1


def test_carry_forward_does_not_use_future_signal(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    write_text(
        paths.project_root / "signals_mixed.jsonl",
        '{"as_of_date":"2024-01-02","generated_at":"2024-01-02T06:00:00Z","region":"CN","signals":{"risk_on":0.1},"source":"global_briefing","version":"v1"}\n'
        '{"as_of_date":"2024-01-04","generated_at":"2024-01-04T06:00:00Z","region":"CN","signals":{"risk_on":0.9},"source":"global_briefing","version":"v1"}\n',
    )

    result = build_global_briefing_replay_bundle(
        "signals_mixed.jsonl",
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-03",
        end_date="2024-01-03",
        allow_carry_forward=True,
        paths=paths,
    )

    assert result["rows"][0]["selected_signal_as_of_date"] == "2024-01-02"


def test_duplicate_same_day_selects_latest_generated_before_decision(tmp_path: Path) -> None:
    result = _build(make_paths(tmp_path), allow_carry_forward=True)

    row = next(item for item in result["rows"] if item["replay_date"] == "2024-01-05")
    assert row["selected_signal_generated_at"] == "2024-01-05T08:30:00Z"
    assert row["signals"]["risk_on"] == 0.3


def test_price_dates_missing_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    with pytest.raises(ValueError, match="price dates missing"):
        build_global_briefing_replay_bundle(
            fixture_path(paths, "signals_valid.jsonl"),
            fixture_path(paths, "prices_valid.csv"),
            start_date="2030-01-01",
            end_date="2030-01-02",
            paths=paths,
        )


def test_signals_missing_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    with pytest.raises(ValueError, match="input file missing"):
        build_global_briefing_replay_bundle(
            "missing.jsonl",
            fixture_path(paths, "prices_valid.csv"),
            start_date="2024-01-02",
            end_date="2024-01-08",
            paths=paths,
        )


def test_bundle_markdown_contains_not_trading_signal(tmp_path: Path) -> None:
    result = _build(make_paths(tmp_path))

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "It is not a trading signal." in report


def test_bundle_does_not_write_orders_trades_portfolio_accounts(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    _build(paths)

    assert_no_protected_paths(paths)


def test_bundle_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(
        [
            "build-global-briefing-replay-bundle",
            "--signals",
            fixture_path(paths, "signals_valid.jsonl"),
            "--prices",
            fixture_path(paths, "prices_valid.csv"),
            "--start-date",
            "2024-01-02",
            "--end-date",
            "2024-01-08",
        ]
    ) == 0


def test_bundle_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(
        [
            "build-global-briefing-replay-bundle",
            "--signals",
            fixture_path(paths, "signals_valid.jsonl"),
            "--prices",
            fixture_path(paths, "prices_valid.csv"),
            "--start-date",
            "2024-01-02",
            "--end-date",
            "2024-01-08",
            "--allow-carry-forward",
        ]
    ) == 0
