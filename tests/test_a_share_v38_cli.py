from a_share_v3x_release_test_utils import AS_OF_DATE, build_through, make_v3x_paths


def test_v38_cli_build_audit_and_component_commands(tmp_path, monkeypatch, capsys):
    from trading_core import cli

    paths = make_v3x_paths(tmp_path)
    build_through(paths, "v37")
    monkeypatch.setattr(cli, "project_paths", lambda: paths)

    assert cli.main(["build-a-share-v38-data-edge-microstructure", "--as-of-date", AS_OF_DATE, "--simulation-only"]) == 0
    assert "overall_passed" in capsys.readouterr().out
    assert cli.main(["audit-a-share-v38-data-edge-microstructure", "--as-of-date", AS_OF_DATE]) == 0
    assert "overall_passed" in capsys.readouterr().out
    for command in [
        "build-a-share-calendar-settlement-edge-review",
        "build-a-share-execution-microstructure-edge-review",
        "build-a-share-financial-pit-edge-review",
    ]:
        assert cli.main([command, "--as-of-date", AS_OF_DATE, "--simulation-only"]) == 0
        assert "overall_passed" in capsys.readouterr().out
