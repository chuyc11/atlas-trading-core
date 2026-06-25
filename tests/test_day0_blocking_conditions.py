from __future__ import annotations

from pathlib import Path

import json
import pytest

from day0_test_utils import make_day0_paths
from trading_core.forward_dry_run.day0_blocking_conditions import REQUIRED_CONDITIONS, build_day0_blocking_conditions
from trading_core.forward_dry_run.day0_data_freeze import build_day0_data_freeze
from trading_core.forward_dry_run.day0_warning_register import build_day0_warning_register


def test_day0_blocking_conditions_all_present_and_clear(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    build_day0_data_freeze(paths=paths)
    build_day0_warning_register(paths=paths)
    result = build_day0_blocking_conditions(paths=paths)
    assert {item["condition_id"] for item in result["conditions"]} == set(REQUIRED_CONDITIONS)
    assert result["current_blocking_count"] == 0
    assert result["manual_confirmation_still_required"] is True
    assert result["boundary"]["forward_dry_run_started"] is False


def test_day0_blocking_conditions_detect_low_coverage_future_and_warning_blocks(tmp_path: Path) -> None:
    paths = make_day0_paths(tmp_path)
    freeze = build_day0_data_freeze(paths=paths)
    freeze["proxy_package"]["coverage_ratio"] = 0.70
    Path(freeze["json_path"]).write_text(json.dumps(freeze), encoding="utf-8")
    warning = build_day0_warning_register(paths=paths)
    warning["blocking_count"] = 1
    Path(warning["json_path"]).write_text(json.dumps(warning), encoding="utf-8")
    gap = paths.data_dir / "system" / "historical_data_gap_closure_audit.json"
    payload = json.loads(gap.read_text(encoding="utf-8"))
    payload["sections"] = {"future_leakage": {"issues": ["future leakage detected"]}}
    gap.write_text(json.dumps(payload), encoding="utf-8")
    result = build_day0_blocking_conditions(paths=paths)
    active = {item["condition_id"] for item in result["conditions"] if item["current_status"]}
    assert {"proxy_coverage_below_0_80", "future_leakage_detected", "warning_register_has_blocking_items"} <= active


def test_day0_blocking_conditions_cli_smoke(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_day0_paths(tmp_path)
    build_day0_data_freeze(paths=paths)
    build_day0_warning_register(paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["day0-blocking-conditions"]) == 0
