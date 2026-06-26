from __future__ import annotations

import json
from pathlib import Path

from trading_core.storage.file_paths import ProjectPaths


def make_a_share_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    for relative in [
        "data/equity_data_quality",
        "data/equity_universe",
        "data/equity_market",
        "data/equity_industry",
        "data/equity_fundamental",
        "outputs/equity_universe",
        "outputs/equity_data_quality",
        "outputs/audit",
        "docs",
    ]:
        (project / relative).mkdir(parents=True, exist_ok=True)
    paths = ProjectPaths(root)
    write_public_snapshot_cache(paths)
    return paths


def write_public_snapshot_cache(paths: ProjectPaths) -> None:
    rows = [
        row("600000", "浦发银行", 8.5, 8.7, 8.4, 8.6, 1000000, 8600000, 0.8, 5.2, 120000000000, 90000000000, 0.65, 19991110),
        row("688001", "华兴源创", 32.1, 33.0, 31.5, 32.6, 500000, 16000000, 1.2, 42.0, 20000000000, 15000000000, 4.3, 20190722),
        row("000001", "平安银行", 10.0, 10.3, 9.9, 10.2, 1500000, 15300000, 0.7, 4.8, 180000000000, 150000000000, 0.72, 19910403),
        row("300750", "宁德时代", 190.0, 195.0, 188.0, 193.0, 800000, 154000000, 0.6, 28.0, 850000000000, 700000000000, 5.2, 20180611),
        row("430047", "诺思兰德", 15.0, 15.5, 14.8, 15.2, 200000, 3040000, 1.1, 30.0, 5000000000, 3000000000, 3.1, 20201124),
        row("830799", "艾融软件", 12.0, 12.4, 11.8, 12.2, 180000, 2196000, 0.9, 24.0, 4200000000, 2500000000, 2.7, 20200727),
    ]
    payload = {
        "snapshot_id": "A-SHARE-PUBLIC-DATA-SNAPSHOT",
        "provider": "local_file_provider",
        "source_timestamp": "2026-06-26T15:30:00Z",
        "rows": rows,
        "attempts": [{"provider": "local_file_provider", "succeeded": True, "reason": ""}],
        "external_api_called": False,
        "real_time_market_data_downloaded": False,
        "provider_reason": "",
        "blocking_reasons": [],
    }
    path = paths.data_dir / "equity_data_quality" / "a_share_public_snapshot_cache.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def row(code, name, open_, high, low, close, volume, amount, turnover, pe, total_mv, circ_mv, pb, list_date):
    return {
        "f12": code,
        "f14": name,
        "f17": open_,
        "f15": high,
        "f16": low,
        "f2": close,
        "f18": open_ - 0.1,
        "f4": close - (open_ - 0.1),
        "f3": 1.2,
        "f5": volume,
        "f6": amount,
        "f8": turnover,
        "f9": pe,
        "f20": total_mv,
        "f21": circ_mv,
        "f23": pb,
        "f26": list_date,
    }


def build_foundation(paths: ProjectPaths):
    from trading_core.equity_data_quality.foundation import build_a_share_data_foundation

    return build_a_share_data_foundation(paths=paths)

