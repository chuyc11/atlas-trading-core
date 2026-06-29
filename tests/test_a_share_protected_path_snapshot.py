from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, write_text
from trading_core.equity_build_repeatability.protected_path_snapshot import (
    build_protected_path_modification_check,
    build_protected_path_snapshot,
)


def test_protected_path_preexisting_directory_allowed(tmp_path):
    paths = make_paths(tmp_path)
    write_text(paths.data_dir / "orders" / "old.jsonl", "old")
    pre = build_protected_path_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_phase="pre_run")
    post = build_protected_path_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_phase="post_run")
    check = build_protected_path_modification_check(as_of_date=AS_OF_DATE, pre_snapshot=pre, post_snapshot=post)
    assert check["overall_passed"] is True
    assert "data/orders" in check["preexisting_protected_paths"]


def test_protected_path_new_file_blocks(tmp_path):
    paths = make_paths(tmp_path)
    pre = build_protected_path_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_phase="pre_run")
    write_text(paths.data_dir / "orders" / "new.jsonl", "new")
    post = build_protected_path_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_phase="post_run")
    check = build_protected_path_modification_check(as_of_date=AS_OF_DATE, pre_snapshot=pre, post_snapshot=post)
    assert check["overall_passed"] is False
    assert check["protected_files_created"]

