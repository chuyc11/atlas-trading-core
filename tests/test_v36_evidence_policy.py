from pathlib import Path

from trading_core.security.v36_evidence import _network_boundary_scan


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
