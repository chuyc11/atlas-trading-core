from __future__ import annotations

from pathlib import Path

import pytest

from a_share_benchmark_claim_hardening_test_utils import make_claim_paths, write_claim_base_inputs


def test_benchmark_claim_hardening_cli_build_audit_and_combined(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))

    assert cli.main(["build-a-share-benchmark-claim-hardening", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["audit-a-share-benchmark-claim-hardening", "--as-of-date", "2026-07-01"]) == 0
    assert cli.main(["build-and-audit-a-share-benchmark-claim-hardening", "--as-of-date", "2026-07-01"]) == 0


def test_benchmark_claim_hardening_cli_allow_public_refresh_is_audit_visible_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_claim_paths(tmp_path)
    write_claim_base_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert (
        cli.main(
            [
                "build-a-share-benchmark-claim-hardening",
                "--as-of-date",
                "2026-07-01",
                "--allow-public-benchmark-refresh",
            ]
        )
        == 0
    )
    request = paths.data_dir / "equity_benchmark_claim_hardening" / "daily" / "2026-07-01" / "benchmark_claim_hardening_request.json"
    text = request.read_text(encoding="utf-8")

    assert '"allow_public_benchmark_refresh": true' in text
    assert '"allow_public_benchmark_refresh_used": false' in text
    assert '"broker_allowed": false' in text
    assert '"real_account_allowed": false' in text
    assert '"real_orders_allowed": false' in text
