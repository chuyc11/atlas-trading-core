from tests.a_share_v090_rc_test_utils import make_paths, seed_v090_outputs, v090_data


def test_v090_source_trace_sweep_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    sweep = v090_data(paths, "v090_source_trace_sweep_result.json")
    assert sweep["source_trace_sweep_run"] is True
    assert sweep["source_workflow_mode"] == "build_from_existing_data"
