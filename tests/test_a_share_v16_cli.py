from __future__ import annotations

from pathlib import Path

import pytest

from a_share_v16_test_utils import make_v16_paths


def test_v16_cli_build_audit_specialty_commands_and_owner_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v16_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "owner_daily_status_output", lambda **_: '{"known_owner_readiness_state":"blocked"}')

    assert cli.main(["build-a-share-v16-pit-backtest-market-rules", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-point-in-time-data-registry", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-event-driven-backtest-replay", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-market-rule-simulation-review", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-virtual-broker-rule-hardening", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["build-a-share-benchmark-index-source-hardening", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-a-share-backtest-trust-scorecard", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["audit-a-share-v16-pit-backtest-market-rules", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-v16-pit-backtest-market-rules", "--as-of-date", "2026-07-01", "--simulation-only"]) == 0
    assert cli.main(["owner-daily-status", "--as-of-date", "2026-07-01", "--format", "json"]) == 0


def test_v16_cli_requires_simulation_only_flag_for_main_and_replay(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_v16_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v16-pit-backtest-market-rules", "--as-of-date", "2026-07-01"]) == 1
    assert cli.main(["build-a-share-event-driven-backtest-replay", "--as-of-date", "2026-07-01"]) == 1
