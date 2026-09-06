from tests.a_share_gated_build_test_utils import seed_gated_build_inputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_current_day_builds.date_alignment import build_gated_build_date_alignment
from trading_core.equity_current_day_builds.input_availability import build_gated_build_input_availability
from trading_core.equity_current_day_builds.preflight_gate import build_preflight_gate


def _gate(paths):
    availability = build_gated_build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    alignment = build_gated_build_date_alignment(paths=paths, as_of_date=AS_OF_DATE)
    return build_preflight_gate(paths=paths, as_of_date=AS_OF_DATE, input_availability=availability, date_alignment=alignment)


def test_gated_build_preflight_gate_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    assert _gate(paths)["overall_passed"] is True


def test_gated_build_preflight_blocks_failed_data_refresh(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    write_json(paths.data_dir / "equity_data_quality" / "a_share_daily_data_refresh_audit.json", {"overall_passed": False, "as_of_date": AS_OF_DATE, "validation_checks": {}})
    assert _gate(paths)["overall_passed"] is False


def test_gated_build_preflight_blocks_low_health_score(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    write_json(paths.data_dir / "equity_ops_center" / "daily" / AS_OF_DATE / "ops_health_score_card.json", {"score": 40})
    assert _gate(paths)["overall_passed"] is False



def test_gated_build_preflight_blocks_corrupt_alert_file(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    alert_path = paths.data_dir / "equity_owner_monitoring" / "daily" / AS_OF_DATE / "alert_evaluation.json"
    alert_path.parent.mkdir(parents=True, exist_ok=True)
    alert_path.write_text("{not json", encoding="utf-8")

    gate = _gate(paths)

    assert gate["overall_passed"] is False
    assert "monitoring_alert_parse_error" in gate["blocking_reasons"]


def test_gated_build_preflight_blocks_corrupt_ops_history_boundary(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_inputs(paths)
    boundary_path = paths.data_dir / "equity_ops_history" / "daily" / AS_OF_DATE / "ops_history_boundary_check.json"
    boundary_path.parent.mkdir(parents=True, exist_ok=True)
    boundary_path.write_text("{not json", encoding="utf-8")

    gate = _gate(paths)

    assert gate["overall_passed"] is False
    assert "ops_history_boundary_parse_error" in gate["blocking_reasons"]
