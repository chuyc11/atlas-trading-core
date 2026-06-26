"""Download shallow external research repositories for v0.7 intake."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPOS = [
    ("https://github.com/ZhuLinsen/alphasift.git", "alphasift"),
    ("https://github.com/tkfy920/qstock.git", "qstock"),
    ("https://github.com/ZhuLinsen/daily_stock_analysis.git", "daily_stock_analysis"),
    ("https://github.com/guiwzh/stock.git", "stock"),
    ("https://github.com/microsoft/qlib.git", "qlib"),
    ("https://github.com/ZhuLinsen/alphaevo.git", "alphaevo"),
    ("https://github.com/zvtvz/zvt.git", "zvt"),
    ("https://github.com/shidenggui/easytrader.git", "easytrader"),
    ("https://github.com/shidenggui/easyquotation.git", "easyquotation"),
    ("https://github.com/shidenggui/easyquant.git", "easyquant"),
    ("https://github.com/nladuo/THSTrader.git", "THSTrader"),
]


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "external_research"
    root.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped = 0
    failed: list[tuple[str, str]] = []
    for url, directory in REPOS:
        target = root / directory
        if target.exists():
            print(f"SKIP {directory} exists")
            skipped += 1
            continue
        print(f"CLONE {url} -> {target}")
        result = subprocess.run(["git", "clone", "--depth", "1", url, str(target)], cwd=root, check=False)
        if result.returncode == 0:
            downloaded += 1
        else:
            failed.append((directory, url))
    print({"downloaded": downloaded, "skipped": skipped, "failed": failed, "root": str(root)})
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
