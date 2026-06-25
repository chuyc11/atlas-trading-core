from pathlib import Path
import json

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, build_baseline_strategy_stack, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.strategies.baseline_strategy_pack_audit import audit_baseline_strategy_pack


def test_baseline_strategy_pack_audit_passes(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths)
    result = audit_baseline_strategy_pack(start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert result["overall_passed"] is True
    assert result["blocking_reasons"] == []
    assert result["summary"]["strategy_count"] == 3
    assert result["summary"]["strategies_complete"] == 3
    assert result["summary"]["all_strategies_complete"] is True
    assert result["summary"]["recommended_next_version"] == "v0.6.1-daily-workflow-binding"
    assert "v0.6.0-baseline-strategy-pack-audited" in Path(result["report_path"]).read_text(encoding="utf-8")
    assert_no_protected_paths(paths)


def test_baseline_strategy_pack_audit_blocks_missing_artifacts_and_boundaries(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths)
    (paths.data_dir / "strategies" / "baseline_strategy_contract.json").unlink()
    registry_path = paths.data_dir / "strategies" / "baseline_strategy_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["strategies"].pop("defensive_cash_rotation")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    signal_path = paths.data_dir / "strategies" / "signals" / f"baseline_signals-equal_weight_etf_rotation-{TEST_START}-{TEST_END}.jsonl"
    signal_path.unlink()
    replay_path = paths.data_dir / "replays" / "strategies" / "momentum_risk_adjusted_rotation" / f"replay-{TEST_START}-{TEST_END}.json"
    replay_path.unlink()
    report_path = paths.data_dir / "strategies" / "reports" / f"baseline_strategy_report-defensive_cash_rotation-{TEST_START}-{TEST_END}.json"
    report_path.unlink()
    summary_path = paths.data_dir / "strategies" / "baseline_strategy_pack_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["promotion_triggered"] = True
    summary["run_daily_called"] = True
    summary["forward_dry_run_started"] = True
    summary["main_ledger_written"] = True
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    (paths.outputs_dir / "strategies" / "BAD_WORDING.md").write_text(
        "strategy effectiveness proven\nML approved for trading\nLLM approved for trading\nRL approved for trading\n",
        encoding="utf-8",
    )
    result = audit_baseline_strategy_pack(start_date=TEST_START, end_date=TEST_END, paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"])
    for expected in [
        "contract",
        "less than 3 strategies",
        "signals",
        "replay",
        "report",
        "promotion_triggered",
        "run_daily_called",
        "forward_dry_run_started",
        "main_ledger_written",
        "ml approved for trading",
        "llm approved for trading",
        "rl approved for trading",
        "strategy effectiveness proven",
    ]:
        assert expected in joined.lower()


def test_baseline_strategy_pack_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    build_baseline_strategy_stack(paths, start_date="2024-01-02", end_date="2024-12-31")
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-baseline-strategy-pack"]) == 0

