from __future__ import annotations

from pathlib import Path

from a_share_v12_test_utils import make_v12_paths, v12_json
from trading_core.equity_v12_continuous_ops.builder import run_a_share_v12_continuous_ops


def test_v12_run_lock_idempotency_key_and_manual_unlock_guidance(tmp_path: Path) -> None:
    paths = make_v12_paths(tmp_path)
    run_a_share_v12_continuous_ops(paths=paths, simulation_only=True)
    lock = v12_json(paths, "v12_run_lock_and_idempotency_result")

    assert lock["run_lock_and_idempotency_checked"] is True
    assert lock["idempotency_key"] == "a-share-v12-2026-07-01-formal"
    assert lock["duplicate_run_detected"] is False
    assert lock["stale_lock_detected"] is False
    assert lock["manual_unlock_guidance"]
