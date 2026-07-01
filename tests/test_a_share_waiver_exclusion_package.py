from trading_core.equity_owner_evidence_backed_reevaluation_prep.preservation_packages import build_waiver_exclusion_package


def test_waiver_exclusion_package_excludes_auto_and_manual_waivers():
    package = build_waiver_exclusion_package()
    assert package["auto_waiver_allowed"] is False
    assert package["manual_waiver_approval_recorded"] is False
    assert package["waiver_used_to_change_gate_status"] is False

