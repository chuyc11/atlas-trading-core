import pytest

from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths
from trading_core.equity_release_chain import audit_release_artifacts, run_release_artifacts, spec_by_key
from trading_core.equity_release_chain.generic import _release_version_is_at_or_after


@pytest.mark.parametrize(
    ("current", "expected"),
    [
        ("v3.5.0-a-share-source", True),
        ("v3.6.0-a-share-target", True),
        ("v4.0.0-a-share-current", True),
        ("v3.4.9-a-share-old", False),
        ("4.0.0", False),
        ("invalid", False),
    ],
)
def test_v36_release_version_gate_accepts_only_semantic_successors(current, expected):
    assert _release_version_is_at_or_after(current, "v3.5.0-a-share-source") is expected


def test_v36_secret_scan_blocks_high_confidence_secret(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v36")
    secret = component_json(paths, "v36", "v36_secret_scan_result")

    assert result["v35_baseline_verified"] is True
    assert result["secret_scan_result_generated"] is True
    assert result["high_confidence_secret_detected"] is False
    assert result["broker_credential_detected"] is False
    assert secret["artifact_generated"] is True
    assert secret["review_status"] == "passed"


def test_v36_fails_closed_when_scanner_evidence_is_missing(tmp_path):
    paths = make_v3x_paths(tmp_path)
    build_through(paths, "v35")
    (paths.project_root / "data" / "security_evidence" / "v36_security_assessment.json").unlink()
    spec = spec_by_key("v36")
    result = run_release_artifacts(spec, as_of_date="2026-07-01", simulation_only=True, paths=paths)
    audit = audit_release_artifacts(spec=spec, as_of_date="2026-07-01", paths=paths)
    secret = component_json(paths, "v36", "v36_secret_scan_result")

    assert result["overall_passed"] is False
    assert result["assessment_status"] == "not_assessed"
    assert result["high_confidence_secret_detected"] is None
    assert "security_assessment_evidence_missing" in result["blocking_reasons"]
    assert audit["overall_passed"] is False
    assert secret["review_status"] == "not_assessed"
