from pathlib import Path
from unittest.mock import patch

from trading_core.security.v36_evidence import _network_boundary_scan, _secret_scan


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


def test_secret_scan_targets_first_party_code_and_config_not_generated_data(tmp_path: Path) -> None:
    for relative in ("src", "scripts", "tests", "config", ".github", "data", "outputs"):
        (tmp_path / relative).mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    completed = {"returncode": 0, "stdout": '{"version":"1.5.0","results":{}}', "stderr": ""}

    with patch("trading_core.security.v36_evidence._run", return_value=completed) as run:
        result = _secret_scan(tmp_path)

    command = run.call_args.args[0]
    assert "--all-files" not in command
    assert result["status"] == "passed"
    assert result["scan_roots"] == ["src", "scripts", "tests", "config", ".github", "pyproject.toml"]
    assert "data" not in command
    assert "outputs" not in command
