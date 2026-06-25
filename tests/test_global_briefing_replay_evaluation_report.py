from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_briefing_test_utils import assert_no_protected_paths, fixture_path, make_paths, write_json, write_text
from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle
from trading_core.global_briefing.replay_evaluation_report import build_global_briefing_replay_report


def _replay(paths) -> dict:
    bundle = build_global_briefing_replay_bundle(
        fixture_path(paths, "signals_valid.jsonl"),
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        allow_carry_forward=True,
        paths=paths,
    )
    return replay_global_briefing_history(
        bundle["json_path"],
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        paths=paths,
    )


def _evaluation(paths) -> dict:
    replay = _replay(paths)
    return build_global_briefing_replay_report(replay["json_path"], paths=paths)


def test_evaluation_json_generated(tmp_path: Path) -> None:
    result = _evaluation(make_paths(tmp_path))

    assert Path(result["json_path"]).exists()
    assert result["overall_status"] == "research_review_ready"
    assert result["execution"]["mode"] == "isolated"


def test_evaluation_markdown_generated(tmp_path: Path) -> None:
    result = _evaluation(make_paths(tmp_path))

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "# Global Briefing Replay Evaluation" in report


def test_missing_replay_blocks(tmp_path: Path) -> None:
    result = build_global_briefing_replay_report("missing.json", paths=make_paths(tmp_path))

    assert result["overall_status"] == "blocked"
    assert any("missing replay artifact" in item for item in result["blocking_reasons"])


def test_main_ledger_written_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    replay["boundary"]["main_ledger_written"] = True
    path = write_json(paths.project_root / "bad_replay.json", replay)

    result = build_global_briefing_replay_report(str(path), paths=paths)

    assert result["overall_status"] == "blocked"
    assert any("main_ledger_written" in item for item in result["blocking_reasons"])


def test_labels_used_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    replay["boundary"]["labels_used"] = True
    path = write_json(paths.project_root / "bad_replay.json", replay)

    result = build_global_briefing_replay_report(str(path), paths=paths)

    assert any("labels_used" in item for item in result["blocking_reasons"])


def test_ml_shadow_used_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    replay["boundary"]["ml_shadow_used"] = True
    path = write_json(paths.project_root / "bad_replay.json", replay)

    result = build_global_briefing_replay_report(str(path), paths=paths)

    assert any("ml_shadow_used" in item for item in result["blocking_reasons"])


def test_experiments_used_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    replay["boundary"]["experiments_used"] = True
    path = write_json(paths.project_root / "bad_replay.json", replay)

    result = build_global_briefing_replay_report(str(path), paths=paths)

    assert any("experiments_used" in item for item in result["blocking_reasons"])


def test_no_trade_fallback_true_warns(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    bundle = build_global_briefing_replay_bundle(
        fixture_path(paths, "signals_valid.jsonl"),
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        allow_carry_forward=True,
        paths=paths,
    )
    replay = replay_global_briefing_history(
        bundle["json_path"],
        fixture_path(paths, "prices_valid.csv"),
        start_date="2024-01-02",
        end_date="2024-01-08",
        execution_mode="no-trade",
        paths=paths,
    )

    result = build_global_briefing_replay_report(replay["json_path"], paths=paths)

    assert any("no_trade_fallback=true" in item for item in result["warnings"])


def test_missing_isolated_outputs_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    Path(replay["isolated_outputs"]["orders"]).unlink()

    result = build_global_briefing_replay_report(replay["json_path"], paths=paths)

    assert result["overall_status"] == "blocked"
    assert any("isolated outputs" in item for item in result["blocking_reasons"])


def test_valuation_days_mismatch_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    valuations = Path(replay["isolated_outputs"]["valuations"])
    lines = valuations.read_text(encoding="utf-8").splitlines()
    valuations.write_text("\n".join(lines[:1]) + "\n", encoding="utf-8")

    result = build_global_briefing_replay_report(replay["json_path"], paths=paths)

    assert any("valuation days" in item for item in result["blocking_reasons"])


def test_negative_cash_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    account_path = Path(replay["isolated_outputs"]["account"])
    account = json.loads(account_path.read_text(encoding="utf-8"))
    account["cash"] = -1.0
    write_json(account_path, account)

    result = build_global_briefing_replay_report(replay["json_path"], paths=paths)

    assert any("negative cash" in item for item in result["blocking_reasons"])


def test_negative_positions_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    replay = _replay(paths)
    valuations = Path(replay["isolated_outputs"]["valuations"])
    row = json.loads(valuations.read_text(encoding="utf-8").splitlines()[0])
    row["positions"] = [{"symbol": "510300.SH", "quantity": -1}]
    write_text(valuations, json.dumps(row) + "\n")

    result = build_global_briefing_replay_report(replay["json_path"], paths=paths)

    assert any("negative positions" in item for item in result["blocking_reasons"])


def test_report_contains_not_strategy_effectiveness_proof(tmp_path: Path) -> None:
    result = _evaluation(make_paths(tmp_path))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This isolated replay does not prove strategy effectiveness." in report


def test_report_contains_not_forward_dry_run_validation(tmp_path: Path) -> None:
    result = _evaluation(make_paths(tmp_path))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This isolated replay is not forward dry-run validation." in report


def test_report_contains_not_live_trading_readiness(tmp_path: Path) -> None:
    result = _evaluation(make_paths(tmp_path))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "This isolated replay is not live trading readiness." in report


def test_report_contains_isolated_execution_review(tmp_path: Path) -> None:
    result = _evaluation(make_paths(tmp_path))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert "## Isolated Execution Review" in report


def test_evaluation_does_not_write_orders_trades_portfolio_accounts(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)

    _evaluation(paths)

    assert_no_protected_paths(paths)


def test_evaluation_does_not_call_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    replay = _replay(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["global-briefing-replay-report", "--replay", replay["json_path"]]) == 0


def test_evaluation_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    replay = _replay(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["global-briefing-replay-report", "--replay", replay["json_path"]]) == 0
