from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, seed_build_output_dashboard_inputs
from trading_core.equity_build_output_dashboard.status_cards import build_executive_status_card, build_workflow_status_card


def test_build_output_status_cards_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_dashboard_inputs(paths)
    executive = build_executive_status_card(as_of_date=AS_OF_DATE, availability={"overall_passed": True, "warnings": [], "blocking_reasons": [], "gated_build_audit_passed": True, "repeatability_audit_passed": True, "business_output_drift_count": 0, "protected_path_modifications_detected": False}, resolution={"warnings": [], "blocking_reasons": []})
    workflow = build_workflow_status_card(paths=paths, as_of_date=AS_OF_DATE)
    assert executive["source_workflow_mode"] == "build_from_existing_data"
    assert workflow["repeat_build_audit_passed"] is True

