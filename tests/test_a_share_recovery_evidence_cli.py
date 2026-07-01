from tests.a_share_recovery_evidence_test_utils import AS_OF_DATE, make_paths, seed_recovery_evidence_inputs
from trading_core.cli import main


def test_recovery_evidence_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-recovery-evidence-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-recovery-evidence", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-recovery-evidence", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-and-audit-a-share-owner-recovery-evidence", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "A-SHARE-OWNER-RECOVERY-EVIDENCE-AUDIT" in out

