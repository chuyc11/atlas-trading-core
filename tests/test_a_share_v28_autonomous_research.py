from __future__ import annotations

from pathlib import Path

from a_share_release_chain_test_utils import build_release, make_release_paths


def test_v28_autonomous_research_governance_does_not_deploy_live(tmp_path: Path) -> None:
    paths = make_release_paths(tmp_path, "v28")
    spec, result, audit = build_release(paths, "v28")

    assert result["overall_passed"] is True
    assert audit["overall_passed"] is True
    assert result["v27_baseline_verified"] is True
    assert result["experiment_registry_generated"] is True
    assert result["llm_proposal_governance_generated"] is True
    assert result["rl_policy_governance_generated"] is True
    assert result["experiment_decision_deploys_live"] is False
    assert result["research_queue_installs_scheduler"] is False
    assert result["full_pytest_run"] is False
    assert len(spec["markdown_names"]) == 8
