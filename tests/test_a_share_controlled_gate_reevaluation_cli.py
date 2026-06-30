from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, make_paths, seed_controlled_gate_reevaluation_inputs
from trading_core.cli import main


def test_controlled_gate_reevaluation_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-controlled-gate-reevaluation-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-controlled-gate-reevaluation", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-controlled-gate-reevaluation", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-and-audit-a-share-owner-controlled-gate-reevaluation", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "skipped_not_ready" in out

