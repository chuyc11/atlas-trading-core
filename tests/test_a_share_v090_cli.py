from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_inputs
from trading_core.cli import main


def test_v090_cli_smoke_skip_full_pytest_marks_not_releasable(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_v090_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-v090-rc-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-v090-rc", "--as-of-date", AS_OF_DATE, "--skip-full-pytest"]) == 1
    assert main(["audit-a-share-owner-v090-rc", "--as-of-date", AS_OF_DATE]) == 1
    out = capsys.readouterr().out
    assert "full_pytest" in out
