from tests.a_share_recovery_execution_test_utils import AS_OF_DATE, make_paths, seed_recovery_execution_inputs
from trading_core.cli import main


def test_recovery_execution_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_recovery_execution_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-readiness-recovery-execution-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-readiness-recovery-execution", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-readiness-recovery-execution", "--as-of-date", AS_OF_DATE]) == 0
    assert "overall_passed" in capsys.readouterr().out
