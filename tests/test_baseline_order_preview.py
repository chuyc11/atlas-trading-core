from pathlib import Path

import pytest

from baseline_strategy_test_utils import TEST_END, TEST_START, make_baseline_paths
from global_briefing_test_utils import assert_no_protected_paths
from trading_core.storage.jsonl_store import read_jsonl
from trading_core.strategies.baseline_order_preview import build_baseline_order_preview
from trading_core.strategies.baseline_signal_engine import generate_baseline_strategy_signals
from trading_core.strategies.common import STRATEGY_IDS


def test_baseline_order_preview_is_preview_only(tmp_path: Path) -> None:
    paths = make_baseline_paths(tmp_path)
    generate_baseline_strategy_signals(strategy="all", start_date=TEST_START, end_date=TEST_END, paths=paths)
    result = build_baseline_order_preview(strategy="all", execution_mode="isolated", paths=paths)
    assert result["preview_only"] is True
    assert result["executed"] is False
    rejected_reasons = []
    for strategy_id in STRATEGY_IDS:
        rows = read_jsonl(Path(result["paths"][strategy_id]["preview_path"]))
        assert rows
        assert all(row["preview_only"] is True for row in rows)
        assert all(row["executed"] is False for row in rows)
        assert all(row["quantity"] % 100 == 0 for row in rows)
        assert all(row["cash_buffer_applied"] is True for row in rows)
        rejected_reasons.extend(row["reject_reason"] for row in rows if row["status"] == "rejected")
    assert "suspended_order_rejected" in rejected_reasons
    assert_no_protected_paths(paths)


def test_baseline_order_preview_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_baseline_paths(tmp_path)
    generate_baseline_strategy_signals(strategy="all", start_date=TEST_START, end_date=TEST_END, paths=paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    assert cli.main(["build-baseline-order-preview", "--strategy", "all", "--execution-mode", "isolated"]) == 0

