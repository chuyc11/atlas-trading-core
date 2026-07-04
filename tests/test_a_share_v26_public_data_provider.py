from __future__ import annotations

from pathlib import Path

from a_share_release_chain_test_utils import build_release, make_release_paths


def test_v26_public_data_provider_is_public_dry_run_only(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v26")
    spec, result, audit = build_release(paths, "v26")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert result["v25_baseline_verified"] is True
    assert result["provider_adapter_registry_generated"] is True
    assert result["refresh_dry_run_only"] is True
    assert result["broker_adapter_added"] is False
    assert result["private_account_adapter_added"] is False
    assert result["unsafe_import_performed"] is False
    assert result["full_pytest_run"] is False
    assert len(spec["json_names"]) == 13
