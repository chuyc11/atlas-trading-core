from __future__ import annotations

from pathlib import Path

from global_briefing_test_utils import make_paths, write_json, write_text
from trading_core.global_briefing.historical_data_packages import sha256_file


REQUIRED_PACKAGES = [
    "HIST-ETF-OHLCV-CN-HK-V1",
    "HIST-BENCHMARK-INDEX-CN-HK-V1",
    "HIST-FX-USDCNY-V1",
    "HIST-GLOBAL-RISK-VIX-V1",
    "HIST-RATES-LIQUIDITY-V1",
    "HIST-COMMODITY-INFLATION-RISK-V1",
    "HIST-POLICY-UNCERTAINTY-EPU-V1",
    "HIST-OECD-CLI-MACRO-CYCLE-V1",
]


def make_day0_paths(tmp_path: Path):
    paths = make_paths(tmp_path)
    seed_day0_prerequisites(paths)
    return paths


def seed_day0_prerequisites(paths) -> None:
    packages = []
    for package_id in REQUIRED_PACKAGES:
        package_path = paths.data_dir / "global_briefing" / "authorized" / "packages" / f"{package_id}.csv"
        if package_id in {"HIST-ETF-OHLCV-CN-HK-V1", "HIST-BENCHMARK-INDEX-CN-HK-V1"}:
            package_path = paths.data_dir / "market" / "historical" / "authorized" / f"{package_id}.csv"
        write_text(package_path, "date,value\n2024-01-02,1\n")
        provenance_path = paths.data_dir / "global_briefing" / "authorized" / "provenance" / f"{package_id}.json"
        write_json(provenance_path, {"package_id": package_id})
        item = {
            "package_id": package_id,
            "status": "downloaded",
            "source": "fixture",
            "path": str(package_path),
            "row_count": 1,
            "coverage_ratio": 1.0,
            "sha256": sha256_file(package_path),
            "provenance_path": str(provenance_path),
            "warnings": [],
        }
        if package_id == "HIST-POLICY-UNCERTAINTY-EPU-V1":
            item.update({"status": "partial_downloaded", "epu_partial": True, "policy_uncertainty_proxy": True, "official_epu": False})
        if package_id == "HIST-OECD-CLI-MACRO-CYCLE-V1":
            item.update({"source": "authorized_macro_cycle_proxy", "official_oecd_cli": False, "macro_cycle_proxy": True, "not_official_oecd_cli": True})
        packages.append(item)
    packages.append({"package_id": "HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1", "status": "not_configured", "source": "gb_authorized_api", "path": "", "row_count": 0, "coverage_ratio": 0.0, "sha256": None, "provenance_path": None, "warnings": []})
    write_json(paths.data_dir / "system" / "historical_data_download_manifest.json", {"packages": packages})
    write_json(paths.data_dir / "system" / "historical_data_quality_audit.json", {"overall_passed": True, "warnings": [], "proxy_package_coverage_ratio": 0.9490196078431372})
    write_json(paths.data_dir / "system" / "historical_data_gap_closure_audit.json", {"overall_passed": True, "blocking_reasons": [], "warnings": [], "boundary": {"forward_dry_run_validated": False, "promotion_triggered": False, "labels_used": False, "ml_shadow_used": False, "experiments_used": False}})
    write_json(
        paths.data_dir / "system" / "historical_data_gap_closure_report.json",
        {
            "overall_status": "passed",
            "epu": {"current_status": "partial_downloaded", "source": "authorized_policy_uncertainty_proxy"},
            "oecd": {"current_status": "downloaded", "source": "authorized_macro_cycle_proxy"},
            "proxy_coverage_ratio": {"current": 0.9490196078431372},
        },
    )
    write_json(
        paths.data_dir / "system" / "historical_warning_inventory.json",
        {
            "raw_warning_count": 346,
            "grouped_warning_count": 6,
            "unknown_warning_count": 0,
            "top_groups": [
                {"category": "source_download_failed", "severity": "medium", "raw_count": 4, "message_pattern": "source failed"},
                {"category": "missing_signal_component", "severity": "medium", "raw_count": 2, "affected_package": "HIST-POLICY-UNCERTAINTY-EPU-V1", "message_pattern": "epu partial"},
                {"category": "coverage_gap", "severity": "medium", "raw_count": 1, "message_pattern": "coverage gap"},
                {"category": "missing_optional_package", "severity": "medium", "raw_count": 1, "message_pattern": "auth gb not configured"},
                {"category": "missing_price", "severity": "high", "raw_count": 1, "message_pattern": "missing price"},
                {"category": "lot_size_constraint", "severity": "medium", "raw_count": 1, "message_pattern": "lot size"},
            ],
        },
    )
    proxy = paths.data_dir / "global_briefing" / "normalized" / "GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl"
    write_text(proxy, '{"as_of_date":"2024-01-02","signals":{}}\n')


def build_day0_stack(paths) -> None:
    from trading_core.forward_dry_run.day0_blocking_conditions import build_day0_blocking_conditions
    from trading_core.forward_dry_run.day0_data_freeze import build_day0_data_freeze
    from trading_core.forward_dry_run.day0_manual_confirmation import build_day0_manual_confirmation_packet
    from trading_core.forward_dry_run.day0_readiness_report import build_day0_readiness_report
    from trading_core.forward_dry_run.day0_run_daily_preflight import build_day0_run_daily_preflight
    from trading_core.forward_dry_run.day0_warning_register import build_day0_warning_register
    from trading_core.forward_dry_run.operating_calendar import build_forward_dry_run_operating_calendar

    build_day0_data_freeze(paths=paths)
    build_day0_warning_register(paths=paths)
    build_day0_blocking_conditions(paths=paths)
    build_day0_run_daily_preflight(paths=paths)
    build_day0_manual_confirmation_packet(paths=paths)
    build_forward_dry_run_operating_calendar(paths=paths)
    build_day0_readiness_report(paths=paths)
