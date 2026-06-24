"""Strategy experiment registry for tracking all strategy experiments.

This module provides a unified registry for parameter experiments, shadow experiments,
ML shadow experiments, and other strategy research experiments.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from trading_core.storage.file_paths import ProjectPaths, project_paths


ALLOWED_MODES = {"shadow", "offline"}
FORBIDDEN_EXPERIMENT_TYPES = {"broker", "live", "margin", "short"}
REQUIRED_FALSE_CONSTRAINTS = {"write_main_ledger", "allow_active"}
REQUIRED_TRUE_CONSTRAINTS = {"shadow_only"}


class ExperimentValidationError(ValueError):
    """Raised when an experiment config fails validation."""


class ExperimentRegistry:
    """Manages the experiment registry file."""

    def __init__(self, paths: ProjectPaths | None = None) -> None:
        self._paths = paths or project_paths()
        self._data_path = self._paths.data_dir / "experiments" / "experiment_registry.json"
        self._output_path = self._paths.outputs_dir / "experiments" / "EXPERIMENT_REGISTRY.md"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self._data_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        """Load the registry from disk."""
        if not self._data_path.exists():
            return {"experiments": []}
        with open(self._data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, registry: dict[str, Any]) -> None:
        """Save the registry to disk."""
        self._data_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._data_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

    def register(self, experiment_config: dict[str, Any]) -> dict[str, Any]:
        """Register a new experiment.

        Args:
            experiment_config: The experiment configuration dictionary.

        Returns:
            The registered experiment record.

        Raises:
            ExperimentValidationError: If the config fails validation.
        """
        _validate_experiment_config(experiment_config)

        registry = self.load()
        experiment_id = experiment_config["experiment_id"]

        # Check for duplicate experiment_id
        if any(exp["experiment_id"] == experiment_id for exp in registry["experiments"]):
            raise ExperimentValidationError(
                f"experiment_id '{experiment_id}' already exists in registry"
            )

        # Build the experiment record
        experiment_record = {
            "experiment_id": experiment_id,
            "experiment_type": experiment_config.get("experiment_type", "unknown"),
            "strategy_id": experiment_config.get("strategy_id", "unknown"),
            "mode": experiment_config.get("mode", "shadow"),
            "status": "registered",
            "created_at": datetime.now(UTC).isoformat(),
            "description": experiment_config.get("description", ""),
            "parameters": experiment_config.get("parameters", {}),
            "data": experiment_config.get("data", {}),
            "constraints": experiment_config.get("constraints", {}),
        }

        registry["experiments"].append(experiment_record)
        self.save(registry)
        self.write_markdown(registry)
        return experiment_record

    def list_experiments(self) -> list[dict[str, Any]]:
        """List all experiments in the registry."""
        registry = self.load()
        return registry.get("experiments", [])

    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        """Get a single experiment by ID.

        Args:
            experiment_id: The experiment ID to look up.

        Returns:
            The experiment record, or None if not found.
        """
        registry = self.load()
        for exp in registry["experiments"]:
            if exp["experiment_id"] == experiment_id:
                return exp
        return None

    def write_markdown(self, registry: dict[str, Any] | None = None) -> Path:
        """Generate and write the registry markdown report.

        Args:
            registry: Optional registry data. If None, loads from disk.

        Returns:
            Path to the generated markdown file.
        """
        if registry is None:
            registry = self.load()
        markdown = build_registry_markdown(registry)
        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return self._output_path


def _contains_forbidden_keyword(value: str) -> bool:
    """Check if a string contains any forbidden experiment keywords.

    This catches cases where mode is shadow but the name implies a live/broker
    experiment, e.g. experiment_type="live_broker_test".
    """
    value_lower = value.lower()
    for keyword in FORBIDDEN_EXPERIMENT_TYPES:
        if keyword in value_lower:
            return True
    return False


def _validate_experiment_config(config: dict[str, Any]) -> None:
    """Validate an experiment configuration.

    Raises:
        ExperimentValidationError: If validation fails.
    """
    errors: list[str] = []

    # Required fields
    if "experiment_id" not in config:
        errors.append("experiment_id is required")

    # Mode validation
    mode = config.get("mode", "shadow")
    if mode not in ALLOWED_MODES:
        errors.append(
            f"mode must be one of {sorted(ALLOWED_MODES)}, got '{mode}'"
        )

    # Experiment type validation
    exp_type = config.get("experiment_type", "")
    if exp_type.lower() in FORBIDDEN_EXPERIMENT_TYPES:
        errors.append(
            f"experiment_type '{exp_type}' is not allowed (forbidden types: {sorted(FORBIDDEN_EXPERIMENT_TYPES)})"
        )
    if _contains_forbidden_keyword(exp_type):
        errors.append(
            f"experiment_type '{exp_type}' contains forbidden keyword"
        )

    # Strategy ID validation
    strategy_id = config.get("strategy_id", "")
    if _contains_forbidden_keyword(strategy_id):
        errors.append(
            f"strategy_id '{strategy_id}' contains forbidden keyword"
        )

    # Constraints validation
    constraints = config.get("constraints", {})

    for key in REQUIRED_FALSE_CONSTRAINTS:
        if constraints.get(key, False) is not False:
            errors.append(f"constraints.{key} must be false")

    for key in REQUIRED_TRUE_CONSTRAINTS:
        if constraints.get(key, True) is not True:
            errors.append(f"constraints.{key} must be true")

    if errors:
        raise ExperimentValidationError("; ".join(errors))


def load_experiment_config(config_path: str | Path) -> dict[str, Any]:
    """Load an experiment config from a YAML or JSON file.

    Args:
        config_path: Path to the config file (.yaml, .yml, or .json).

    Returns:
        The parsed configuration dictionary.
    """
    path = Path(config_path)
    suffix = path.suffix.lower()

    with open(path, "r", encoding="utf-8") as f:
        if suffix in {".yaml", ".yml"}:
            return yaml.safe_load(f)
        elif suffix == ".json":
            return json.load(f)
        else:
            # Try YAML first, fall back to JSON
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError:
                f.seek(0)
                return json.load(f)


def build_registry_markdown(registry: dict[str, Any]) -> str:
    """Build a markdown report for the experiment registry.

    Args:
        registry: The registry data dictionary.

    Returns:
        Markdown string.
    """
    experiments = registry.get("experiments", [])
    total = len(experiments)
    by_status: dict[str, int] = {}
    for exp in experiments:
        status = exp.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1

    lines = [
        "# Experiment Registry",
        "",
        f"**Total experiments:** {total}",
        "",
    ]

    if by_status:
        lines.append("## Status Summary")
        lines.append("")
        for status, count in sorted(by_status.items()):
            lines.append(f"- **{status}**: {count}")
        lines.append("")

    lines.append("## Experiments")
    lines.append("")

    if not experiments:
        lines.append("_No experiments registered yet._")
    else:
        # Table header
        lines.append(
            "| Experiment ID | Type | Strategy | Mode | Status | Created | Description |"
        )
        lines.append("|---|---|---|---|---|---|---|")

        # Sort by created_at descending
        sorted_exps = sorted(
            experiments,
            key=lambda e: e.get("created_at", ""),
            reverse=True,
        )

        for exp in sorted_exps:
            exp_id = exp.get("experiment_id", "")
            exp_type = exp.get("experiment_type", "")
            strategy = exp.get("strategy_id", "")
            mode = exp.get("mode", "")
            status = exp.get("status", "")
            created = exp.get("created_at", "")[:10]  # Just the date
            desc = exp.get("description", "").replace("|", "\\|")
            if len(desc) > 60:
                desc = desc[:57] + "..."
            lines.append(
                f"| {exp_id} | {exp_type} | {strategy} | {mode} | {status} | {created} | {desc} |"
            )

    lines.append("")
    return "\n".join(lines)


# Convenience functions
def register_experiment(
    config_path: str | Path,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    """Register an experiment from a config file.

    Args:
        config_path: Path to the experiment config file.
        paths: Optional project paths.

    Returns:
        The registered experiment record.
    """
    config = load_experiment_config(config_path)
    registry = ExperimentRegistry(paths)
    return registry.register(config)


def list_experiments(paths: ProjectPaths | None = None) -> list[dict[str, Any]]:
    """List all experiments.

    Args:
        paths: Optional project paths.

    Returns:
        List of experiment records.
    """
    registry = ExperimentRegistry(paths)
    return registry.list_experiments()


def get_experiment(
    experiment_id: str,
    paths: ProjectPaths | None = None,
) -> dict[str, Any] | None:
    """Get an experiment by ID.

    Args:
        experiment_id: The experiment ID.
        paths: Optional project paths.

    Returns:
        The experiment record, or None if not found.
    """
    registry = ExperimentRegistry(paths)
    return registry.get_experiment(experiment_id)


def load_registry(paths: ProjectPaths | None = None) -> dict[str, Any]:
    """Load the full registry.

    Args:
        paths: Optional project paths.

    Returns:
        The registry dictionary.
    """
    registry = ExperimentRegistry(paths)
    return registry.load()


def save_registry(registry: dict[str, Any], paths: ProjectPaths | None = None) -> None:
    """Save the registry and update markdown.

    Args:
        registry: The registry dictionary.
        paths: Optional project paths.
    """
    reg = ExperimentRegistry(paths)
    reg.save(registry)
    reg.write_markdown(registry)
