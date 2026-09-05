from pathlib import Path
from unittest.mock import patch

from trading_core.security.v36_evidence import _network_boundary_scan, _secret_scan
import pytest

pytestmark = pytest.mark.smoke


def test_network_policy_allows_exact_sse_host_and_rejects_lookalike(tmp_path: Path) -> None:
    source = tmp_path / "src"
    source.mkdir()
    (source / "allowed.py").write_text('URL = "https://www.sse.com.cn/market/calendar"\n', encoding="utf-8")
    (source / "rejected.py").write_text('URL = "https://www.sse.com.cn.evil.test/calendar"\n', encoding="utf-8")

    result = _network_boundary_scan(tmp_path)

    assert "www.sse.com.cn" in result["allowed_hosts"]
    assert result["status"] == "failed"
    assert result["findings"] == [{
        "path": "src/rejected.py",
        "line": 1,
        "url": "https://www.sse.com.cn.evil.test",
        "host": "www.sse.com.cn.evil.test",
        "rule": "network_host_not_allowlisted",
    }]


def test_secret_scan_splits_source_entropy_from_generated_data(tmp_path: Path) -> None:
    for relative in ("src", "scripts", "tests", "config", ".github", "data", "outputs"):
        (tmp_path / relative).mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    completed = {"returncode": 0, "stdout": '{"version":"1.5.0","results":{}}', "stderr": ""}

    not_a_repository = {"returncode": 1, "stdout": "", "stderr": "not a git repository"}
    with patch(
        "trading_core.security.v36_evidence._run",
        side_effect=[completed, not_a_repository],
    ) as run:
        result = _secret_scan(tmp_path)

    assert run.call_count == 2
    source_command = run.call_args_list[0].args[0]
    assert run.call_args_list[1].args[0] == ["git", "rev-parse", "--is-inside-work-tree"]
    artifact_command = result["commands"][1]
    assert "--all-files" in source_command
    assert "src" in source_command and "tests" in source_command
    assert "HexHighEntropyString" not in source_command
    assert "data" in artifact_command and "outputs" in artifact_command
    assert artifact_command[0] == "atlas-artifact-credential-policy"
    assert result["status"] == "passed"
    assert result["scan_profiles"][0]["entropy_plugins_enabled"] is True
    assert result["scan_profiles"][1]["entropy_plugins_enabled"] is False
    assert result["scanned_all_in_scope_files"] is True
    assert result["excluded_roots"]["generated_evidence"] == ["data/security_evidence"]


def test_secret_scan_does_not_treat_its_own_manifest_hash_as_a_secret(tmp_path: Path) -> None:
    for relative in ("src", "scripts", "tests", "config", ".github", "data/security_evidence", "outputs"):
        (tmp_path / relative).mkdir(parents=True)
    (tmp_path / "src" / "safe.py").write_text("VALUE = 'safe'\n", encoding="utf-8")
    (tmp_path / "data" / "security_evidence" / "v36_scope_manifest.json").write_text(
        '{"sha256":"' + ("4f8c" * 16) + '"}\n',
        encoding="utf-8",
    )

    result = _secret_scan(tmp_path)

    assert result["status"] == "passed"
    assert result["unreviewed_finding_count"] == 0


def test_artifact_profile_detects_credential_formats_without_hash_entropy_noise(tmp_path: Path) -> None:
    for relative in ("src", "scripts", "tests", "config", ".github", "data", "outputs"):
        (tmp_path / relative).mkdir(parents=True)
    (tmp_path / "src" / "safe.py").write_text("VALUE = 'safe'\n", encoding="utf-8")
    (tmp_path / "data" / "hashes.json").write_text(
        '{"sha256":"' + ("4f8c" * 16) + '"}\n',
        encoding="utf-8",
    )
    (tmp_path / "outputs" / "leak.json").write_text(
        '{"api_key":"sk-' + ("A1b2" * 8) + '"}\n'
        'password=testSuperSecret\n'
        'password=test\n',
        encoding="utf-8",
    )

    result = _secret_scan(tmp_path)

    assert result["status"] == "failed"
    assert result["unreviewed_finding_count"] == 2
    assert result["findings"][0]["profile"] == "data_outputs"
    assert result["findings"][0]["filename"] == "outputs/leak.json"
