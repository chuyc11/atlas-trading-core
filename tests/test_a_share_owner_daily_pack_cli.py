from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_inputs
from trading_core import cli


def test_owner_daily_pack_cli_smoke(tmp_path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["validate-a-share-owner-daily-pack-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-a-share-owner-daily-pack", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-owner-daily-pack", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-owner-daily-pack", "--as-of-date", AS_OF_DATE]) == 0
