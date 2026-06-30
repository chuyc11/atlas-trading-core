from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_inputs
from trading_core import cli


def test_build_output_ops_cli_smoke(tmp_path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_build_output_ops_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    assert cli.main(["validate-a-share-build-output-ops-refresh-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-a-share-build-output-ops-refresh", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-build-output-ops-refresh", "--as-of-date", AS_OF_DATE]) == 0
