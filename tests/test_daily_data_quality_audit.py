from pathlib import Path
import json

import pytest

from daily_workflow_test_utils import AS_OF, make_daily_workflow_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.daily_workflow.daily_data_quality_audit import audit_daily_data_quality
from trading_core.daily_workflow.daily_market_data_snapshot import build_daily_market_data_snapshot


def test_daily_data_quality_audit_passes(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    snapshot = build_daily_market_data_snapshot(as_of_date=AS_OF, paths=paths)
    result = audit_daily_data_quality(snapshot=f"data/daily_workflow/snapshots/daily_market_data_snapshot-{AS_OF}.json", paths=paths)
    assert result["overall_passed"] is True
    assert result["summary"]["symbols_total"] == 8
    assert result["summary"]["symbols_complete"] == 8
    assert result["summary"]["benchmark_available"] is True
    assert result["summary"]["risk_proxy_available"] is True
    assert result["boundary"]["external_download_called"] is False
    assert result["boundary"]["run_daily_called"] is False
    assert Path(result["json_path"]).exists()
    assert Path(result["report_path"]).exists()
    assert_no_protected_paths(paths)


def test_daily_data_quality_audit_blocks_missing_snapshot_and_symbol(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    missing = audit_daily_data_quality(snapshot="data/daily_workflow/snapshots/missing.json", paths=paths)
    assert missing["overall_passed"] is False
    snapshot = build_daily_market_data_snapshot(as_of_date=AS_OF, paths=paths)
    snapshot_path = Path(snapshot["json_path"])
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    payload["symbols"]["510300.SH"]["available"] = False
    snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    result = audit_daily_data_quality(snapshot=str(snapshot_path), paths=paths)
    assert result["overall_passed"] is False
    assert "510300.SH missing" in "\n".join(result["blocking_reasons"])


def test_daily_data_quality_audit_missing_benchmark_and_risk(tmp_path: Path) -> None:
    paths = make_daily_workflow_paths(tmp_path)
    snapshot = build_daily_market_data_snapshot(as_of_date=AS_OF, paths=paths)
    snapshot_path = Path(snapshot["json_path"])
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    for item in payload["benchmarks"].values():
        item["available"] = False
    payload["risk_proxy_available"] = False
    snapshot_path.write_text(json.dumps(payload), encoding="utf-8")
    result = audit_daily_data_quality(snapshot=str(snapshot_path), paths=paths)
    assert result["overall_passed"] is False
    joined = "\n".join(result["blocking_reasons"])
    assert "no benchmark available" in joined
    assert "risk proxy missing" in joined


def test_daily_data_quality_audit_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_daily_workflow_paths(tmp_path)
    build_daily_market_data_snapshot(as_of_date=AS_OF, paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["audit-daily-data-quality", "--snapshot", f"data/daily_workflow/snapshots/daily_market_data_snapshot-{AS_OF}.json"]) == 0

