from tests.a_share_owner_quality_exception_test_utils import make_paths, seed_owner_quality_exception_outputs
from trading_core.equity_owner_quality_exceptions.quality_exception_audit import audit_a_share_owner_quality_exceptions


def test_quality_exception_audit_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    audit = audit_a_share_owner_quality_exceptions(paths=paths)
    assert audit["overall_passed"] is True
    assert audit["exception_checks"]["blocked_gate_decision_preserved"] is True


def test_quality_exception_audit_fails_when_auto_waiver_true(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    record = paths.data_dir / "equity_owner_quality_exceptions" / "daily" / "2026-06-26" / "manual_waiver_decision_record.json"
    import json

    payload = json.loads(record.read_text(encoding="utf-8"))
    payload["auto_waiver_allowed"] = True
    record.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    audit = audit_a_share_owner_quality_exceptions(paths=paths)
    assert audit["overall_passed"] is False
    assert "auto_waiver_false" in audit["blocking_reasons"]
