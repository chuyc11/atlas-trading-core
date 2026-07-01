from tests.a_share_operator_experience_test_utils import AS_OF_DATE, make_paths, seed_operator_inputs
from trading_core.cli import main


def test_operator_experience_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_operator_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-operator-experience-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-operator-experience", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-operator-experience", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "blocked" in out
