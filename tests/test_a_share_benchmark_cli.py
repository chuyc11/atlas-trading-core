from __future__ import annotations

from pathlib import Path

import pytest

from a_share_benchmark_test_utils import make_benchmark_paths
from a_share_feature_test_utils import AS_OF_DATE


def test_benchmark_cli_smoke_no_run_daily(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from trading_core import cli

    paths = make_benchmark_paths(tmp_path)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)
    monkeypatch.setattr(cli, "run_daily", lambda _date: (_ for _ in ()).throw(AssertionError("run_daily called")))
    monkeypatch.setattr(
        cli,
        "build_a_share_benchmark_comparison",
        lambda **_: {
            "builder_id": "b",
            "as_of_date": AS_OF_DATE,
            "benchmark_data_availability": {
                "benchmarks": [
                    {"benchmark_id": key, "status": "available"}
                    for key in ["CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_STRICT_TRADABLE", "EQUAL_WEIGHT_CANDIDATE_POOL"]
                ]
            },
            "relative_performance_snapshot": {"limited_history_flagged": True, "performance_not_yet_observed": True},
            "benchmark_summary": {"recommended_next_version": "v0.7.11-a-share-multi-day-portfolio-performance-tracking"},
        },
    )
    monkeypatch.setattr(
        cli,
        "audit_a_share_benchmark_comparison",
        lambda **_: {
            "audit_id": "a",
            "overall_passed": True,
            "blocking_reasons": [],
            "warnings": [],
            "benchmark_availability_checks": dict.fromkeys(["CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_STRICT_TRADABLE", "EQUAL_WEIGHT_CANDIDATE_POOL"], "available"),
            "comparison_checks": {"limited_history_correctly_flagged": True, "performance_not_fabricated": True},
            "recommended_next_version": "v0.7.11-a-share-multi-day-portfolio-performance-tracking",
            "json_path": "j",
            "report_path": "r",
        },
    )

    assert cli.main(["build-a-share-benchmark-comparison", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["audit-a-share-benchmark-comparison", "--as-of-date", AS_OF_DATE]) == 0
    assert cli.main(["build-and-audit-a-share-benchmark-comparison", "--as-of-date", AS_OF_DATE]) == 0
