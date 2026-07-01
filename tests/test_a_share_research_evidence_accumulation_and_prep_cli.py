from tests.a_share_research_evidence_test_utils import AS_OF_DATE, make_paths, seed_research_evidence_inputs
from trading_core.cli import build_parser, main


def test_research_evidence_cli_commands_registered():
    parser = build_parser()
    assert parser.parse_args(["build-a-share-research-evidence-accumulation-and-prep", "--as-of-date", AS_OF_DATE]).command == "build-a-share-research-evidence-accumulation-and-prep"
    assert parser.parse_args(["audit-a-share-research-evidence-accumulation-and-prep", "--as-of-date", AS_OF_DATE]).command == "audit-a-share-research-evidence-accumulation-and-prep"
    assert parser.parse_args(["build-and-audit-a-share-research-evidence-accumulation-and-prep", "--as-of-date", AS_OF_DATE]).command == "build-and-audit-a-share-research-evidence-accumulation-and-prep"


def test_research_evidence_cli_build_audit_smoke(tmp_path, monkeypatch, capsys):
    import trading_core.cli as cli

    paths = make_paths(tmp_path)
    seed_research_evidence_inputs(paths)
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert main(["build-a-share-research-evidence-accumulation-and-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-RESEARCH-EVIDENCE-ACCUMULATION-AND-PREP" in capsys.readouterr().out
    assert main(["audit-a-share-research-evidence-accumulation-and-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert "A-SHARE-RESEARCH-EVIDENCE-ACCUMULATION-AND-PREP-AUDIT" in capsys.readouterr().out
    assert main(["build-and-audit-a-share-research-evidence-accumulation-and-prep", "--as-of-date", AS_OF_DATE]) == 0
    assert "audit_overall_passed" in capsys.readouterr().out
