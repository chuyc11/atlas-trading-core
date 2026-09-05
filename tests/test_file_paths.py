from pathlib import Path

import pytest

from trading_core.storage.file_paths import find_workspace_root, project_paths

pytestmark = pytest.mark.smoke


def test_path_discovery_prefers_composite_workspace_layout(tmp_path: Path) -> None:
    project = tmp_path / "work" / "trading-core"
    start = project / "src" / "trading_core" / "storage" / "file_paths.py"
    start.parent.mkdir(parents=True)
    start.write_text("", encoding="utf-8")

    paths = project_paths(tmp_path)

    assert find_workspace_root(start) == tmp_path
    assert paths.workspace_root == tmp_path
    assert paths.project_root == project
    assert paths.global_briefing_data_dir == tmp_path / "work" / "global-briefing" / "data"


def test_path_discovery_supports_standalone_repository_checkout(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='trading-core'\n", encoding="utf-8")
    package = tmp_path / "src" / "trading_core"
    package.mkdir(parents=True)
    start = package / "module.py"
    start.write_text("", encoding="utf-8")

    paths = project_paths(tmp_path)

    assert find_workspace_root(start) == tmp_path
    assert paths.workspace_root == tmp_path
    assert paths.project_root == tmp_path
    assert paths.data_dir == tmp_path / "data"
    assert paths.outputs_dir == tmp_path / "outputs"


def test_path_discovery_fails_closed_without_known_layout(tmp_path: Path) -> None:
    start = tmp_path / "unknown" / "module.py"
    start.parent.mkdir()
    start.write_text("", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="unable to discover"):
        find_workspace_root(start)
