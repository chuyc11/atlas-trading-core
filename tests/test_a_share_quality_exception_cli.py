from tests.a_share_owner_quality_exception_test_utils import AS_OF_DATE, make_paths, seed_owner_quality_exception_inputs
from trading_core import cli


def test_quality_exception_cli_smoke(tmp_path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    assert cli.main(["validate-a-share-owner-quality-exceptions-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-owner-quality-exceptions", "--as-of-date", AS_OF_DATE]) == 0
