from tests.a_share_final_closeout_test_utils import AS_OF_DATE
from tests.a_share_research_evidence_test_utils import make_paths, seed_research_evidence_inputs
from trading_core.cli import build_parser, main
from trading_core.equity_research_evidence_accumulation import (
    audit_a_share_research_evidence_accumulation_and_prep,
    build_a_share_research_evidence_accumulation_and_prep,
)


def test_final_closeout_cli_commands_registered():
    parser = build_parser()
    assert parser.parse_args(["build-a-share-final-not-ready-closeout", "--as-of-date", AS_OF_DATE]).command == "build-a-share-final-not-ready-closeout"
    assert parser.parse_args(["audit-a-share-final-not-ready-closeout", "--as-of-date", AS_OF_DATE]).command == "audit-a-share-final-not-ready-closeout"
    assert parser.parse_args(["build-and-audit-a-share-final-not-ready-closeout", "--as-of-date", AS_OF_DATE]).command == "build-and-audit-a-share-final-not-ready-closeout"


def test_final_closeout_cli_build_audit_smoke(tmp_path, monkeypatch, capsys):
    import trading_core.cli as cli

    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    build_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)
    audit_a_share_research_evidence_accumulation_and_prep(paths=paths, as_of_date=AS_OF_DATE)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert main(["build-a-share-final-not-ready-closeout", "--as-of-date", AS_OF_DATE]) == 0
    assert "final_not_ready_closeout" in capsys.readouterr().out
    assert main(["audit-a-share-final-not-ready-closeout", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-FINAL-NOT-READY-CLOSEOUT-AUDIT" in capsys.readouterr().out
    assert main(["build-and-audit-a-share-final-not-ready-closeout", "--as-of-date", AS_OF_DATE]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out
