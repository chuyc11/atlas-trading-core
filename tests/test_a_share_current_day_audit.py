from tests.a_share_current_day_test_utils import AS_OF_DATE, fake_workflow_audit, make_paths, seed_data_refresh
from trading_core.equity_current_day.current_day_audit import audit_a_share_current_day_research_run
from trading_core.equity_current_day import current_day_runner


def test_current_day_audit_passes_for_generated_run(tmp_path, monkeypatch):
    paths = make_paths(tmp_path)
    seed_data_refresh(paths)
    monkeypatch.setattr(current_day_runner, "run_a_share_daily_research_workflow", lambda **kwargs: {"workflow_id": "ok"})
    monkeypatch.setattr(current_day_runner, "audit_a_share_daily_research_workflow", lambda **kwargs: fake_workflow_audit())
    current_day_runner.run_a_share_current_day_research(as_of_date=AS_OF_DATE, paths=paths)
    audit = audit_a_share_current_day_research_run(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["workflow_checks"]["workflow_audit_passed"] is True

