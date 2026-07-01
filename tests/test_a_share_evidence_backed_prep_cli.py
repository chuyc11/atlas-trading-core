from tests.a_share_evidence_backed_prep_test_utils import AS_OF_DATE, make_paths, seed_evidence_backed_prep_inputs
from trading_core.cli import main


def test_evidence_backed_prep_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-evidence-backed-reevaluation-prep-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-evidence-backed-reevaluation-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-evidence-backed-reevaluation-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-and-audit-a-share-owner-evidence-backed-reevaluation-prep", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "A-SHARE-OWNER-EVIDENCE-BACKED-REEVALUATION-PREP-AUDIT" in out

