from __future__ import annotations

from pathlib import Path

import pytest

from global_briefing_test_utils import fixture_path, make_paths, write_json
from trading_core.global_briefing.historical_replay_runner import replay_global_briefing_history
from trading_core.global_briefing.isolated_replay_adapter_audit import RELEASE_CANDIDATE, audit_isolated_replay_adapter
from trading_core.global_briefing.replay_bundle_builder import build_global_briefing_replay_bundle
from trading_core.global_briefing.replay_evaluation_report import build_global_briefing_replay_report


def _artifacts(paths) -> dict:
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
        execution_mode="isolated",
        paths=paths,
    )
    evaluation = build_global_briefing_replay_report(replay["json_path"], paths=paths)
    return {"bundle": bundle, "replay": replay, "evaluation": evaluation}


def _audit(paths) -> dict:
    artifacts = _artifacts(paths)
    return audit_isolated_replay_adapter(replay_path=artifacts["replay"]["json_path"], evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)


def test_audit_json_generated(tmp_path: Path) -> None:
    result = _audit(make_paths(tmp_path))

    assert Path(result["json_path"]).exists()
    assert result["overall_passed"] is True


def test_audit_markdown_generated(tmp_path: Path) -> None:
    result = _audit(make_paths(tmp_path))

    assert "# Isolated Replay Adapter Audit" in Path(result["report_path"]).read_text(encoding="utf-8")


def test_execution_mode_not_isolated_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["execution"]["mode"] = "no-trade"
    path = write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_isolated_replay_adapter(replay_path=str(path), evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("execution.mode" in item for item in result["blocking_reasons"])


def test_no_trade_fallback_true_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["execution"]["no_trade_fallback"] = True
    path = write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_isolated_replay_adapter(replay_path=str(path), evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("no_trade_fallback" in item for item in result["blocking_reasons"])


def test_missing_account_output_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["replay"]["isolated_outputs"]["account"]).unlink()

    result = audit_isolated_replay_adapter(replay_path=artifacts["replay"]["json_path"], evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("account" in item for item in result["blocking_reasons"])


def test_missing_orders_output_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["replay"]["isolated_outputs"]["orders"]).unlink()

    result = audit_isolated_replay_adapter(replay_path=artifacts["replay"]["json_path"], evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("orders" in item for item in result["blocking_reasons"])


def test_missing_trades_output_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["replay"]["isolated_outputs"]["trades"]).unlink()

    result = audit_isolated_replay_adapter(replay_path=artifacts["replay"]["json_path"], evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("trades" in item for item in result["blocking_reasons"])


def test_missing_valuations_output_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["replay"]["isolated_outputs"]["valuations"]).unlink()

    result = audit_isolated_replay_adapter(replay_path=artifacts["replay"]["json_path"], evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("valuations" in item for item in result["blocking_reasons"])


def test_isolated_output_outside_allowed_root_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    outside = write_json(paths.project_root / "outside-account.json", {"ok": True})
    artifacts["replay"]["isolated_outputs"]["account"] = str(outside)
    path = write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_isolated_replay_adapter(replay_path=str(path), evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("outside data/replays/global_briefing" in item for item in result["blocking_reasons"])


def test_boundary_true_values_block(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    for key in [
        "main_ledger_written",
        "run_daily_called",
        "labels_used",
        "ml_shadow_used",
        "experiments_used",
        "promotion_triggered",
        "forward_dry_run",
        "live_trading",
        "broker_connected",
    ]:
        artifacts["replay"]["boundary"][key] = True
    path = write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_isolated_replay_adapter(replay_path=str(path), evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    for key in ["main_ledger_written", "run_daily_called", "labels_used", "ml_shadow_used", "experiments_used", "promotion_triggered", "forward_dry_run", "live_trading"]:
        assert any(key in item for item in result["blocking_reasons"])


def test_forbidden_wording_live_trading_ready_blocks(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    Path(artifacts["replay"]["report_path"]).write_text("live trading ready\n", encoding="utf-8")

    result = audit_isolated_replay_adapter(replay_path=artifacts["replay"]["json_path"], evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)

    assert any("wording" in item for item in result["blocking_reasons"])


def test_overall_passed_recommends_v055_tag(tmp_path: Path) -> None:
    result = _audit(make_paths(tmp_path))
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is True
    assert RELEASE_CANDIDATE in report


def test_overall_failed_does_not_recommend_tag(tmp_path: Path) -> None:
    paths = make_paths(tmp_path)
    artifacts = _artifacts(paths)
    artifacts["replay"]["execution"]["no_trade_fallback"] = True
    path = write_json(Path(artifacts["replay"]["json_path"]), artifacts["replay"])

    result = audit_isolated_replay_adapter(replay_path=str(path), evaluation_path=artifacts["evaluation"]["json_path"], paths=paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is False
    assert RELEASE_CANDIDATE not in report


def test_adapter_audit_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_paths(tmp_path)
    _artifacts(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["audit-isolated-replay-adapter"]) == 0
