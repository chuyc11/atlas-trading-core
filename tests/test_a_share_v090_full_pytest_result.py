from trading_core.equity_owner_v090_rc.full_pytest_result import (
    build_full_pytest_result,
    build_skipped_full_pytest_result,
    is_reusable_full_pytest_result,
    parse_pytest_counts,
)


def test_v090_full_pytest_result_parsing_and_failure_blocking():
    assert parse_pytest_counts("22 passed, 1 skipped in 1.2s") == (22, 0, 1)
    passed = build_full_pytest_result(exit_code=0, stdout="123 passed, 2 skipped in 3s", stderr="", duration_seconds=3)
    assert passed["overall_passed"] is True
    assert passed["passed_count"] == 123
    failed = build_full_pytest_result(exit_code=1, stdout="1 failed, 122 passed in 3s", stderr="", duration_seconds=3)
    assert failed["overall_passed"] is False
    assert "full_pytest_failed" in failed["blocking_reasons"]
    skipped = build_skipped_full_pytest_result()
    assert skipped["overall_passed"] is False
    assert "full_pytest_skipped_not_releasable" in skipped["blocking_reasons"]


def test_v090_full_pytest_reuse_requires_real_passed_execution():
    passed = build_full_pytest_result(exit_code=0, stdout="123 passed in 3s", stderr="", duration_seconds=3)
    assert is_reusable_full_pytest_result(passed)
    skipped = build_skipped_full_pytest_result()
    assert not is_reusable_full_pytest_result(skipped)
    failed = build_full_pytest_result(exit_code=1, stdout="1 failed in 3s", stderr="", duration_seconds=3)
    assert not is_reusable_full_pytest_result(failed)
