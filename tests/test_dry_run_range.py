from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from trading_core.storage.jsonl_store import read_json, write_json, write_jsonl


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_dry_run_range.py"


def _load_dry_run_module() -> Any:
    spec = importlib.util.spec_from_file_location("run_dry_run_range", SCRIPT_PATH)
    assert spec
    assert spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed_inputs(root: Path) -> None:
    data_dir = root / "work" / "global-briefing" / "data"
    write_jsonl(
        data_dir / "macro_signals-2026-06-23.jsonl",
        [
            {
                "macro_signal_id": "MACRO-20260623-001",
                "date": "2026-06-23",
                "region": "CHINA",
                "theme": "policy_support",
                "scenario": "Policy support favors CSI 300 ETF exposure",
                "confidence": "medium",
                "affected_assets": ["510300.SH"],
                "risk_flags": [],
                "status": "open",
            }
        ],
    )
    write_json(
        data_dir / "china-market-snapshot-2026-06-23.json",
        {
            "provider": "test",
            "items": [
                {"symbol": "510300.SH", "market": "A_SHARE", "price": 4.0, "previous_close": 3.98, "data_status": "ok"},
                {"symbol": "000300.SH", "market": "A_SHARE_INDEX", "price": 5000.0, "previous_close": 4980.0, "data_status": "ok"},
            ],
        },
    )
    write_json(
        data_dir / "china-market-snapshot-2026-06-25.json",
        {
            "provider": "test",
            "items": [
                {"symbol": "510300.SH", "market": "A_SHARE", "price": 4.1, "previous_close": 4.0, "data_status": "ok"},
                {"symbol": "000300.SH", "market": "A_SHARE_INDEX", "price": 5030.0, "previous_close": 5000.0, "data_status": "ok"},
            ],
        },
    )


def test_dry_run_range_writes_summary_and_survives_missing_inputs(
    workspace_with_calendar: Path,
) -> None:
    module = _load_dry_run_module()
    _seed_inputs(workspace_with_calendar)

    result = module.run_dry_run_range(
        "2026-06-23",
        "2026-06-25",
        workspace_root=workspace_with_calendar,
    )

    report_path = Path(result["report_path"])
    json_path = Path(result["json_path"])
    report = report_path.read_text(encoding="utf-8")
    payload = read_json(json_path)

    assert report_path.name == "DRY_RUN_SUMMARY-2026-06-23-2026-06-25.md"
    assert payload["scheduled_trading_days"] == 3
    assert payload["total_run_days"] == 3
    assert payload["success_days"] == 3
    assert payload["missing_input_count"] >= 3
    assert payload["total_signals_count"] == 3
    assert payload["asset_curve"]
    assert "Total signals" in report
    assert "Missing input files" in report
