from trading_core.equity_owner_closeout_review.closeout_config import BUILD_RC_SCOPE, CloseoutReviewConfig, validate_config


def test_closeout_review_config_defaults_and_mode_validation():
    config = CloseoutReviewConfig()
    payload = config.to_dict(
        source_gate_decision="blocked",
        selected_v0820_branch="final_blocked_closeout",
        previous_readiness_score=54,
        minimum_owner_readiness_score=75,
        score_gap=21,
    )
    assert config.mode == BUILD_RC_SCOPE
    assert payload["closeout_review_only"] is True
    assert payload["generate_new_gate_score"] is False
    assert validate_config(CloseoutReviewConfig(mode="bad")) == [
        "mode must be one of ['validate_closeout_review_inputs', 'review_owner_readiness_closeout_lineage', 'build_v090_rc_scope', 'build_v090_full_regression_plan', 'build_closeout_review_report', 'audit_existing_closeout_review']"
    ]
