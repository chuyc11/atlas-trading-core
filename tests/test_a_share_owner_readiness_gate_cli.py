from tests.a_share_owner_readiness_gate_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_gate_inputs
from trading_core import cli


def test_owner_readiness_gate_cli_smoke(tmp_path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    assert cli.main(["validate-a-share-owner-readiness-gate-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-owner-readiness-gate", "--as-of-date", AS_OF_DATE]) == 0
