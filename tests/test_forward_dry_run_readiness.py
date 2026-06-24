"""Tests for forward dry-run readiness audit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.forward_dry_run_readiness import RELEASE_CANDIDATE, run_forward_dry_run_readiness


@pytest.fixture
def readiness_paths(tmp_path: Path) -> ProjectPaths:
    workspace = tmp_path
    project = workspace / "work" / "trading-core"
    _write_text(project / "VERSION", "v0.5.2-usability-polish")
    _write_text(project / "README.md", "research-only\nnot live trading ready\n")
    _write_text(project / "RELEASE_NOTES.md", "v0.5.2-usability-polish\nno live trading\n")
    _write_text(
        project / "docs" / "FORWARD_DRY_RUN_RUNBOOK.md",
        "30 day forward dry-run remains incomplete\n"
        "Do not replace forward dry-run with historical replay\n"
        "Historical replay is not forward dry-run.\n",
    )
    _write_text(project / "docs" / "SAFETY_BOUNDARY.md", "Historical replay is not forward dry-run.\nNo broker.\n")
    _write_text(project / "docs" / "RUNBOOK.md", "run-daily command documented\n")
    _write_text(project / "docs" / "CLI_REFERENCE.md", "run-daily\n")
    _write_text(
        project / "docs" / "ARTIFACT_MAP.md",
        "Artifacts are not broker instructions and not permission to trade.\n"
        "backtests replays shadow experiments reports system\n"
        "no artifact writes main forward ledger\n",
    )
    for name in ["universe_china_etf.yaml", "benchmarks.yaml", "risk_rules.yaml"]:
        _write_text(project / "config" / name, "ok: true\n")
    _write_text(project / "src" / "trading_core" / "daily_run.py", "from trading_core.signals.signal_generator import generate_trading_signals\n")
    _write_text(project / "src" / "trading_core" / "signals" / "signal_generator.py", "def generate_trading_signals(): pass\n")
    _write_text(project / "src" / "trading_core" / "broker" / "virtual_broker.py", "def process_signals(): pass\n")
    return ProjectPaths(workspace_root=workspace)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_readiness_json_generated(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert Path(result["json_path"]).exists()
    assert result["overall_passed"] is True


def test_readiness_markdown_generated(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    report = Path(result["report_path"]).read_text(encoding="utf-8")
    assert "# Forward Dry-Run Readiness Audit" in report


def test_day0_checklist_generated(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    checklist = Path(result["day0_checklist_path"]).read_text(encoding="utf-8")
    assert "Forward Dry-Run Day-0 Checklist" in checklist
    assert "No ML shadow in run-daily" in checklist


def test_30d_plan_generated(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    plan = Path(result["plan_path"]).read_text(encoding="utf-8")
    assert "Forward Dry-Run 30 Trading-Day Plan" in plan
    assert "python -m trading_core.cli run-daily --date YYYY-MM-DD" in plan


def test_missing_forward_runbook_strict_blocks(readiness_paths: ProjectPaths) -> None:
    (readiness_paths.project_root / "docs" / "FORWARD_DRY_RUN_RUNBOOK.md").unlink()

    result = run_forward_dry_run_readiness(strict=True, paths=readiness_paths)

    assert result["overall_passed"] is False
    assert any("required_docs" in reason for reason in result["blocking_reasons"])


def test_missing_trading_calendar_warns_not_blocking(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(calendar="data/calendar/trading_calendar.json", paths=readiness_paths)

    assert result["overall_passed"] is True
    assert result["warnings"]


def test_protected_path_snapshot_unchanged(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    snapshot = result["sections"]["protected_path_snapshot"]
    assert snapshot["passed"] is True
    assert snapshot["modified_paths"] == []


def test_audit_does_not_create_orders_trades_portfolio_accounts(readiness_paths: ProjectPaths) -> None:
    run_forward_dry_run_readiness(paths=readiness_paths)

    for raw in ["data/orders", "data/trades", "data/portfolio", "data/accounts", "outputs/orders", "outputs/trades", "outputs/portfolio"]:
        assert not (readiness_paths.project_root / raw).exists()


def test_run_daily_import_labels_blocks(readiness_paths: ProjectPaths) -> None:
    _write_text(readiness_paths.project_root / "src" / "trading_core" / "daily_run.py", "from trading_core.labels.label_store import build_label_matrix\n")

    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["overall_passed"] is False
    assert any("run_daily_isolation" in reason for reason in result["blocking_reasons"])


def test_run_daily_import_ml_shadow_blocks(readiness_paths: ProjectPaths) -> None:
    _write_text(readiness_paths.project_root / "src" / "trading_core" / "daily_run.py", "from trading_core.ml.shadow_model import train_ml_shadow_model\n")

    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["overall_passed"] is False
    assert any("run_daily_isolation" in reason for reason in result["blocking_reasons"])


def test_run_daily_import_experiments_blocks(readiness_paths: ProjectPaths) -> None:
    _write_text(readiness_paths.project_root / "src" / "trading_core" / "daily_run.py", "from trading_core.experiments.parameter_sweep import run_parameter_sweep_from_config\n")

    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["overall_passed"] is False
    assert any("run_daily_isolation" in reason for reason in result["blocking_reasons"])


def test_label_store_in_signal_generator_blocks(readiness_paths: ProjectPaths) -> None:
    _write_text(readiness_paths.project_root / "src" / "trading_core" / "signals" / "signal_generator.py", "from trading_core.labels import label_store\n")

    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["overall_passed"] is False
    assert any("label_store used in signal generator" in reason for reason in result["blocking_reasons"])


def test_ml_shadow_predictions_in_order_generation_blocks(readiness_paths: ProjectPaths) -> None:
    _write_text(readiness_paths.project_root / "src" / "trading_core" / "broker" / "virtual_broker.py", "ml_shadow_predictions = []\n")

    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["overall_passed"] is False
    assert any("ML shadow predictions used in order generation" in reason for reason in result["blocking_reasons"])


def test_historical_replay_not_forward_wording_is_accepted(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["sections"]["future_data_leakage_readiness"]["passed"] is True


def test_report_contains_readiness_only(readiness_paths: ProjectPaths) -> None:
    report = Path(run_forward_dry_run_readiness(paths=readiness_paths)["report_path"]).read_text(encoding="utf-8")

    assert "This audit is readiness-only." in report


def test_report_contains_does_not_start_forward_dry_run(readiness_paths: ProjectPaths) -> None:
    report = Path(run_forward_dry_run_readiness(paths=readiness_paths)["report_path"]).read_text(encoding="utf-8")

    assert "This audit does not start forward dry-run." in report


def test_report_contains_does_not_validate_forward_dry_run(readiness_paths: ProjectPaths) -> None:
    report = Path(run_forward_dry_run_readiness(paths=readiness_paths)["report_path"]).read_text(encoding="utf-8")

    assert "This audit does not validate forward dry-run." in report


def test_report_contains_not_live_trading_ready(readiness_paths: ProjectPaths) -> None:
    report = Path(run_forward_dry_run_readiness(paths=readiness_paths)["report_path"]).read_text(encoding="utf-8")

    assert "This system is not live trading ready." in report


def test_report_contains_labels_must_not_be_used(readiness_paths: ProjectPaths) -> None:
    report = Path(run_forward_dry_run_readiness(paths=readiness_paths)["report_path"]).read_text(encoding="utf-8")

    assert "Labels must not be used in run-daily." in report


def test_report_contains_historical_replay_boundary(readiness_paths: ProjectPaths) -> None:
    report = Path(run_forward_dry_run_readiness(paths=readiness_paths)["report_path"]).read_text(encoding="utf-8")

    assert "Historical replay is not forward dry-run." in report


def test_overall_passed_recommends_v053_tag(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is True
    assert RELEASE_CANDIDATE in report


def test_overall_failed_does_not_recommend_tag(readiness_paths: ProjectPaths) -> None:
    _write_text(readiness_paths.project_root / "README.md", "live trading ready\n")

    result = run_forward_dry_run_readiness(paths=readiness_paths)
    report = Path(result["report_path"]).read_text(encoding="utf-8")

    assert result["overall_passed"] is False
    assert RELEASE_CANDIDATE not in report


def test_does_not_call_run_daily(readiness_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    monkeypatch.setattr(cli, "project_paths", lambda: readiness_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["forward-dry-run-readiness"]) == 0


def test_boundary_flags_false(readiness_paths: ProjectPaths) -> None:
    result = run_forward_dry_run_readiness(paths=readiness_paths)

    assert result["boundary"]["run_daily_called"] is False
    assert result["boundary"]["forward_dry_run_started"] is False
    assert result["boundary"]["forward_dry_run_validated"] is False
    assert result["boundary"]["orders_written"] is False
    assert result["boundary"]["trades_written"] is False
    assert result["boundary"]["portfolio_written"] is False
    assert result["boundary"]["accounts_written"] is False


def test_cli_smoke_with_calendar(readiness_paths: ProjectPaths, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    calendar = readiness_paths.project_root / "data" / "calendar" / "trading_calendar.json"
    calendar.parent.mkdir(parents=True)
    calendar.write_text(json.dumps({"trading_days": ["2026-06-26", "2026-06-29"]}), encoding="utf-8")
    monkeypatch.setattr(cli, "project_paths", lambda: readiness_paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["forward-dry-run-readiness", "--start-date", "2026-06-26", "--trading-days", "2", "--calendar", "data/calendar/trading_calendar.json"]) == 0
