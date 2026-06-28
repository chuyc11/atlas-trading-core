"""Input loading for v0.7.7 A-share daily stock selection briefing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from trading_core.equity_briefings.briefing_config import DEFAULT_AS_OF_DATE
from trading_core.equity_portfolios.portfolio_config import PORTFOLIO_FILES
from trading_core.equity_scoring.score_config import SCORE_FILES
from trading_core.equity_selection.candidate_config import CANDIDATE_FILES
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


@dataclass(frozen=True)
class BriefingInputs:
    as_of_date: str
    requested_as_of_date: str
    candidate_dir: Path
    score_dir: Path
    feature_dir: Path
    portfolio_dir: Path
    candidate_manifest_path: Path
    score_manifest_path: Path
    feature_manifest_path: Path
    portfolio_manifest_path: Path
    candidate_manifest: dict[str, Any]
    score_manifest: dict[str, Any]
    feature_manifest: dict[str, Any]
    portfolio_manifest: dict[str, Any]
    candidate_summary: dict[str, Any]
    score_summary: dict[str, Any]
    feature_summary: dict[str, Any]
    portfolio_weight_summary: dict[str, Any]
    portfolio_industry_exposure: dict[str, Any]
    portfolio_risk_liquidity_summary: dict[str, Any]
    long_candidates: list[dict[str, Any]]
    mid_candidates: list[dict[str, Any]]
    short_candidates: list[dict[str, Any]]
    multi_horizon_candidates: list[dict[str, Any]]
    risk_downgraded_candidates: list[dict[str, Any]]
    long_virtual_portfolio: list[dict[str, Any]]
    mid_virtual_portfolio: list[dict[str, Any]]
    short_virtual_portfolio: list[dict[str, Any]]
    candidate_audit: dict[str, Any]
    score_audit: dict[str, Any]
    feature_audit: dict[str, Any]
    portfolio_audit: dict[str, Any]


def briefing_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_briefings" / "daily" / as_of_date


def briefing_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_briefings" / "daily" / as_of_date


def load_briefing_inputs(
    *,
    paths: ProjectPaths | None = None,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    allow_latest_artifact_date: bool = False,
) -> BriefingInputs:
    paths = default_paths(paths)
    selected_date = _resolve_artifact_date(paths, as_of_date, allow_latest_artifact_date)
    candidate_dir = paths.data_dir / "equity_selection" / "daily" / selected_date
    score_dir = paths.data_dir / "equity_scores" / "daily" / selected_date
    feature_dir = paths.data_dir / "equity_features" / "daily" / selected_date
    portfolio_dir = paths.data_dir / "equity_portfolios" / "daily" / selected_date
    candidate_manifest_path = candidate_dir / CANDIDATE_FILES["candidate_manifest"]
    score_manifest_path = score_dir / SCORE_FILES["score_manifest"]
    feature_manifest_path = feature_dir / "feature_manifest.json"
    portfolio_manifest_path = portfolio_dir / PORTFOLIO_FILES["portfolio_manifest"]
    return BriefingInputs(
        as_of_date=selected_date,
        requested_as_of_date=as_of_date,
        candidate_dir=candidate_dir,
        score_dir=score_dir,
        feature_dir=feature_dir,
        portfolio_dir=portfolio_dir,
        candidate_manifest_path=candidate_manifest_path,
        score_manifest_path=score_manifest_path,
        feature_manifest_path=feature_manifest_path,
        portfolio_manifest_path=portfolio_manifest_path,
        candidate_manifest=_load_dict(candidate_manifest_path),
        score_manifest=_load_dict(score_manifest_path),
        feature_manifest=_load_dict(feature_manifest_path),
        portfolio_manifest=_load_dict(portfolio_manifest_path),
        candidate_summary=_load_dict(candidate_dir / CANDIDATE_FILES["candidate_generation_summary"]),
        score_summary=_load_dict(score_dir / SCORE_FILES["scoring_summary"]),
        feature_summary=_load_dict(feature_dir / "feature_generation_summary.json"),
        portfolio_weight_summary=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_weight_summary"]),
        portfolio_industry_exposure=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_industry_exposure"]),
        portfolio_risk_liquidity_summary=_load_dict(portfolio_dir / PORTFOLIO_FILES["portfolio_risk_liquidity_summary"]),
        long_candidates=_load_list(candidate_dir / CANDIDATE_FILES["long_candidates_json"]),
        mid_candidates=_load_list(candidate_dir / CANDIDATE_FILES["mid_candidates_json"]),
        short_candidates=_load_list(candidate_dir / CANDIDATE_FILES["short_candidates_json"]),
        multi_horizon_candidates=_load_list(candidate_dir / CANDIDATE_FILES["multi_horizon_candidates"]),
        risk_downgraded_candidates=_load_list(candidate_dir / CANDIDATE_FILES["risk_downgraded_candidates"]),
        long_virtual_portfolio=_load_list(portfolio_dir / PORTFOLIO_FILES["long_virtual_portfolio_json"]),
        mid_virtual_portfolio=_load_list(portfolio_dir / PORTFOLIO_FILES["mid_virtual_portfolio_json"]),
        short_virtual_portfolio=_load_list(portfolio_dir / PORTFOLIO_FILES["short_virtual_portfolio_json"]),
        candidate_audit=_load_dict(paths.data_dir / "equity_data_quality" / "a_share_candidate_generation_audit.json"),
        score_audit=_load_dict(paths.data_dir / "equity_data_quality" / "a_share_scoring_audit.json"),
        feature_audit=_load_dict(paths.data_dir / "equity_data_quality" / "a_share_multi_horizon_feature_audit.json"),
        portfolio_audit=_load_dict(paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_construction_audit.json"),
    )


def _resolve_artifact_date(paths: ProjectPaths, as_of_date: str, allow_latest: bool) -> str:
    if _has_required_inputs(paths, as_of_date):
        return as_of_date
    if not allow_latest:
        raise ValueError(f"briefing inputs not found for as_of_date={as_of_date}")
    base = paths.data_dir / "equity_selection" / "daily"
    candidates = sorted(path.name for path in base.glob("*") if path.is_dir() and path.name <= as_of_date and _has_required_inputs(paths, path.name))
    if not candidates:
        raise ValueError(f"no briefing input package available on or before {as_of_date}")
    return candidates[-1]


def _has_required_inputs(paths: ProjectPaths, as_of_date: str) -> bool:
    candidate_dir = paths.data_dir / "equity_selection" / "daily" / as_of_date
    score_dir = paths.data_dir / "equity_scores" / "daily" / as_of_date
    portfolio_dir = paths.data_dir / "equity_portfolios" / "daily" / as_of_date
    required = [
        candidate_dir / CANDIDATE_FILES["candidate_manifest"],
        candidate_dir / CANDIDATE_FILES["long_candidates_json"],
        candidate_dir / CANDIDATE_FILES["mid_candidates_json"],
        candidate_dir / CANDIDATE_FILES["short_candidates_json"],
        candidate_dir / CANDIDATE_FILES["multi_horizon_candidates"],
        candidate_dir / CANDIDATE_FILES["risk_downgraded_candidates"],
        score_dir / SCORE_FILES["score_manifest"],
        score_dir / SCORE_FILES["scoring_summary"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_manifest"],
        portfolio_dir / PORTFOLIO_FILES["long_virtual_portfolio_json"],
        portfolio_dir / PORTFOLIO_FILES["mid_virtual_portfolio_json"],
        portfolio_dir / PORTFOLIO_FILES["short_virtual_portfolio_json"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_industry_exposure"],
        portfolio_dir / PORTFOLIO_FILES["portfolio_risk_liquidity_summary"],
    ]
    return all(path.exists() for path in required)


def _load_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _load_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []
