from tests.a_share_owner_closeout_review_test_utils import AS_OF_DATE, make_paths, seed_closeout_inputs
from trading_core.cli import main


def test_closeout_review_cli_smoke(tmp_path, capsys, monkeypatch):
    paths = make_paths(tmp_path)
    seed_closeout_inputs(paths)
    monkeypatch.setattr("trading_core.cli.project_paths", lambda: paths)
    assert main(["validate-a-share-owner-closeout-review-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-a-share-owner-closeout-review", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["audit-a-share-owner-closeout-review", "--as-of-date", AS_OF_DATE]) == 0
    assert main(["build-and-audit-a-share-owner-closeout-review", "--as-of-date", AS_OF_DATE]) == 0
    out = capsys.readouterr().out
    assert "A-SHARE-OWNER-CLOSEOUT-REVIEW-AUDIT" in out
