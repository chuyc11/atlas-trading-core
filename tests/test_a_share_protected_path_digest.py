from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from tests.a_share_owner_dashboard_test_utils import write_json
from trading_core.equity_owner_daily_pack.protected_path_digest import build_protected_path_digest


def test_protected_path_digest_distinguishes_preexisting_from_modified(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    write_json(
        paths.data_dir / "equity_build_repeatability" / "daily" / AS_OF_DATE / "protected_path_modification_check.json",
        {
            "preexisting_protected_paths": ["data/orders"],
            "protected_path_modifications_detected": False,
            "protected_files_modified": [],
            "protected_files_created": [],
            "protected_files_deleted": [],
        },
    )
    write_json(
        paths.data_dir / "equity_build_output_dashboard" / "daily" / AS_OF_DATE / "build_output_protected_path_card.json",
        {"preexisting_protected_paths": ["data/orders"]},
    )

    digest = build_protected_path_digest(paths=paths, as_of_date=AS_OF_DATE)

    assert digest["digest_id"] == "A-SHARE-PROTECTED-PATH-DIGEST"
    assert digest["preexisting_protected_paths"]
    assert digest["protected_path_modifications_detected"] is False
    assert digest["protected_files_modified"] == []
