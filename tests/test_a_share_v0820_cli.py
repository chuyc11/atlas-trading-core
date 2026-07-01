from tests.a_share_v0820_test_utils import AS_OF_DATE, make_paths, seed_v0820_inputs
from trading_core.cli import main


def test_v0820_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_v0820_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-v0820-gate-outcome-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-v0820-gate-outcome", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-v0820-gate-outcome", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-and-audit-a-share-owner-v0820-gate-outcome", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "A-SHARE-OWNER-V0820-GATE-OUTCOME-AUDIT" in out

