import json

from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs
from trading_core.equity_owner_daily_pack.daily_pack_audit import audit_a_share_owner_daily_pack


def test_owner_operations_decision_pack_is_not_investment_pack(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)
    pack_path = paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "owner_operations_decision_pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))

    assert pack["decision_pack_type"] == "owner_operations_decision_pack"
    assert pack["not_investment_decision_pack"] is True
    assert pack["next_operational_decision"] in {
        "no_action_required",
        "review_warnings",
        "review_safe_actions",
        "inspect_artifacts",
        "wait_for_more_history",
        "developer_follow_up",
        "rerun_audit_only",
        "hold_release",
    }


def test_owner_operations_decision_pack_forbidden_category_blocks_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)
    pack_path = paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "owner_operations_decision_pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    pack["forbidden_decision_categories_detected"] = ["buy_stock"]
    pack_path.write_text(json.dumps(pack, ensure_ascii=False), encoding="utf-8")

    audit = audit_a_share_owner_daily_pack(as_of_date=AS_OF_DATE, paths=paths)

    assert audit["overall_passed"] is False
    assert "no_forbidden_decision_categories" in audit["blocking_reasons"]
