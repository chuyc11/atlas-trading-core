from __future__ import annotations

import json
from pathlib import Path

from a_share_benchmark_claim_hardening_test_utils import claim_data_dir, make_claim_paths, write_claim_base_inputs
from trading_core.equity_benchmark_claim_hardening.audit import audit_a_share_benchmark_claim_hardening
from trading_core.equity_benchmark_claim_hardening.builder import build_a_share_benchmark_claim_hardening


def test_benchmark_claim_hardening_audit_passes_clean_build_and_protected_boundaries(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)
    build_a_share_benchmark_claim_hardening(paths=paths)

    audit = audit_a_share_benchmark_claim_hardening(paths=paths)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["boundary"]["broker_connected"] is False
    assert audit["boundary"]["real_account_data_read"] is False
    assert audit["boundary"]["real_orders_placed"] is False
    assert audit["boundary"]["real_order_preview_generated"] is False
    assert audit["boundary"]["buy_sell_signals_generated"] is False
    assert audit["boundary"]["owner_readiness_gate_rerun"] is False
    assert audit["boundary"]["new_gate_score_generated"] is False
    assert audit["boundary"]["new_gate_decision_generated"] is False


def test_benchmark_claim_hardening_audit_catches_fabricated_metrics(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)
    build_a_share_benchmark_claim_hardening(paths=paths)
    path = claim_data_dir(paths) / "csi_benchmark_attribution_result.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["benchmarks"][0]["excess_return"] = 0.12
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    audit = audit_a_share_benchmark_claim_hardening(paths=paths)

    assert audit["overall_passed"] is False
    assert "fabrication_flag_true" in audit["blocking_reasons"]


def test_benchmark_claim_hardening_audit_catches_missing_guard_result(tmp_path: Path) -> None:
    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)
    build_a_share_benchmark_claim_hardening(paths=paths)
    (claim_data_dir(paths) / "performance_claim_guard_result.json").unlink()

    audit = audit_a_share_benchmark_claim_hardening(paths=paths)

    assert audit["overall_passed"] is False
    assert "performance_claim_guard_result" in audit["blocking_reasons"]
    assert "performance_claim_guard_missing" in audit["blocking_reasons"]
