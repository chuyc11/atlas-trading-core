from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, fixture_path, make_paths
from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle


def _bundle(paths, *, allow_carry_forward: bool = False) -> dict:
    return build_global_briefing_replay_bundle(
        fixture_path(paths, "signals_valid.jsonl"),
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        allow_carry_forward=allow_carry_forward,
        paths=paths,
    )


def _replay(paths, *, allow_carry_forward: bool = False) -> dict:
    bundle = _bundle(paths, allow_carry_forward=allow_carry_forward)
    return replay_global_briefing_history(
        bundle["json_path"],
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
    )


def test_valid_bundle_generates_replay_summary(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path), allow_carry_forward=True)

    assert Path(result["json_path"]).exists()
    assert result["summary"]["days_processed"] == 5
    assert result["isolated"] is True
    assert result["execution"]["mode"] == "isolated"


def test_replay_writes_only_isolated_global_briefing_directory(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = _replay(paths, allow_carry_forward=True)

    for output_path in result["isolated_outputs"].values():
        assert "data\\replays\\global_briefing" in output_path or "data/replays/global_briefing" in output_path
    assert_no_protected_paths(paths)


def test_main_orders_trades_portfolio_accounts_unchanged(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    result = _replay(paths)

    assert result["boundary"]["main_ledger_written"] is False
    assert result["protected_path_changes"] == []


def test_replay_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    bundle = _bundle(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(
        [
            "replay-global-briefing-history",
            "--bundle",
            bundle["json_path"],
            "--prices",
            fixture_path(paths, "prices_valid.csv"),
            "--start-date",
            "2024-01-02",
            "--end-date",
            "2024-01-08",
        ]
    ) == 0


def test_labels_ml_and_experiments_not_used(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path))

    assert result["boundary"]["labels_used"] is False
    assert result["boundary"]["ml_shadow_used"] is False
    assert result["boundary"]["experiments_used"] is False


def test_missing_bundle_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    with pytest.raises(ValueError, match="bundle file missing"):
        replay_global_briefing_history(
            "missing.json",
            fixture_path(paths, "prices_valid.csv"),
            start_date="2024-01-02",
            end_date="2024-01-08",
            paths=paths,
        )


def test_missing_prices_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    bundle = _bundle(paths)

    with pytest.raises(ValueError, match="prices file missing"):
        replay_global_briefing_history(
            bundle["json_path"],
            "missing.csv",
            start_date="2024-01-02",
            end_date="2024-01-08",
            paths=paths,
        )


def test_missing_signal_days_enter_data_quality(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path), allow_carry_forward=False)

    assert "2024-01-04" in result["data_quality"]["missing_signal_days"]


def test_isolated_mode_generates_signals_orders_trades_valuations_and_account(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path), allow_carry_forward=True)

    assert result["summary"]["signals"] > 0
    assert result["summary"]["orders"] > 0
    assert result["summary"]["trades"] > 0
    assert result["summary"]["valuations"] == 5
    for key in ["account", "signals", "orders", "trades", "portfolio", "valuations"]:
        assert Path(result["isolated_outputs"][key]).exists()


def test_isolated_mode_no_trade_fallback_false(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path), allow_carry_forward=True)

    assert result["execution"]["no_trade_fallback"] is False
    assert result["boundary"]["isolated_replay_ledger_written"] is True


def test_no_trade_mode_still_available(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    bundle = _bundle(paths, allow_carry_forward=True)

    result = replay_global_briefing_history(
        bundle["json_path"],
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        execution_mode="no-trade",
        paths=paths,
    )

    assert result["execution"]["mode"] == "no-trade"
    assert result["execution"]["no_trade_fallback"] is True
    assert result["summary"]["orders"] == 0


def test_replay_markdown_contains_not_forward_dry_run(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path))

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "It is not forward dry-run." in report


def test_replay_markdown_contains_main_ledger_not_written(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path))

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "- main ledger not written" in report


def test_replay_markdown_contains_isolated_replay_ledger_only(tmp_path: Path) -> None:
    result = _replay(make_paths(tmp_path), allow_carry_forward=True)

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "- isolated replay ledger only" in report


def test_replay_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    bundle = _bundle(paths, allow_carry_forward=True)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(
        [
            "replay-global-briefing-history",
            "--bundle",
            bundle["json_path"],
            "--prices",
            fixture_path(paths, "prices_valid.csv"),
            "--start-date",
            "2024-01-02",
            "--end-date",
            "2024-01-08",
            "--execution-mode",
            "isolated",
        ]
    ) == 0
