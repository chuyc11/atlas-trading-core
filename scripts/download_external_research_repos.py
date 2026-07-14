"""Download immutable external research repositories for v0.7 intake."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPOS = [
    ("https://github.com/ZhuLinsen/alphasift.git", "alphasift", "9f522747caafd3c0b1ddb7e14d5cf44c8580b6cf"),
    ("https://github.com/tkfy920/qstock.git", "qstock", "d710191e93184c51e14be036127511dac0df2a36"),
    ("https://github.com/ZhuLinsen/daily_stock_analysis.git", "daily_stock_analysis", "55946536a9765b3d4e2620edef6a50e79d0928d0"),
    ("https://github.com/guiwzh/stock.git", "stock", "14289d0cef90fa2e59b8c99c350f47aa362aaa18"),
    ("https://github.com/microsoft/qlib.git", "qlib", "d5379c520f66a39953bad76234a7019a72796fd0"),
    ("https://github.com/ZhuLinsen/alphaevo.git", "alphaevo", "712e60b3a79fa3835ac725e91e4f5b2c5811f652"),
    ("https://github.com/zvtvz/zvt.git", "zvt", "8509990e6608750d0c08fa748682cc997d2813cc"),
    ("https://github.com/shidenggui/easytrader.git", "easytrader", "def5a8edc5ebd7d49bf92a9f39e9e30c9bf47101"),
    ("https://github.com/shidenggui/easyquotation.git", "easyquotation", "7778c1b9f93afb2ce2cf431de393fe690d4ec07c"),
    ("https://github.com/shidenggui/easyquant.git", "easyquant", "bb5f0a1c21230bd421f7f8627c05817cff75c737"),
    ("https://github.com/nladuo/THSTrader.git", "THSTrader", "fe07e879c6196ce63515e36594d37a03b085970d"),
]


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True, text=True, timeout=120)


def main() -> int:
    root = Path(__file__).resolve().parents[1] / "external_research"
    root.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    skipped = 0
    failed: list[tuple[str, str]] = []
    for url, directory, commit in REPOS:
        target = root / directory
        if target.exists():
            current = git("rev-parse", "HEAD", cwd=target) if (target / ".git").is_dir() else None
            if current and current.returncode == 0 and current.stdout.strip().lower() == commit:
                print(f"SKIP {directory} already pinned at {commit}")
                skipped += 1
            else:
                print(f"FAIL {directory} exists but is not pinned at {commit}")
                failed.append((directory, url))
            continue
        print(f"FETCH {url}@{commit} -> {target}")
        target.mkdir()
        commands = [
            git("init", cwd=target),
            git("remote", "add", "origin", url, cwd=target),
            git("fetch", "--depth", "1", "origin", commit, cwd=target),
            git("checkout", "--detach", commit, cwd=target),
        ]
        current = git("rev-parse", "HEAD", cwd=target)
        if all(result.returncode == 0 for result in commands) and current.returncode == 0 and current.stdout.strip().lower() == commit:
            downloaded += 1
        else:
            failed.append((directory, url))
    print({"downloaded": downloaded, "skipped": skipped, "failed": failed, "root": str(root)})
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
