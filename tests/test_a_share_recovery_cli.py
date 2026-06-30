from tests.a_share_owner_readiness_recovery_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_recovery_inputs
from trading_core.cli import main


def test_a_share_recovery_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-readiness-recovery-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-readiness-recovery", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-readiness-recovery", "--as-of-date", AS_OF_DATE]) == 0
    assert "overall_passed" in capsys.readouterr().out
