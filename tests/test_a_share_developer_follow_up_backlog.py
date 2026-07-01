from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_developer_follow_up_backlog_links_requirements(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    backlog = final_json(paths, "developer_follow_up_backlog")

    assert backlog["item_count"] >= 3
    assert backlog["blocking_item_count"] >= 1
    assert all(item["recommended_version"].startswith("v0.9.7") for item in backlog["items"])
    assert all("owner_readiness_gate_rerun" in item["forbidden_scope"] for item in backlog["items"])
