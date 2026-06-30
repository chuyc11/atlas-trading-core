from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_inputs
from trading_core import cli


def test_owner_daily_pack_history_cli_smoke(tmp_path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    assert cli.main(["validate-a-share-owner-daily-pack-history-inputs", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-a-share-owner-daily-pack-history", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-owner-daily-pack-history", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-owner-daily-pack-history", "--as-of-date", AS_OF_DATE]) == 0
