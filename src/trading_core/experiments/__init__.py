"""Strategy experiment registry and parameter sweep module."""

from trading_core.experiments.experiment_registry import (
    ExperimentRegistry,
    register_experiment,
    list_experiments,
    get_experiment,
    build_registry_markdown,
    load_registry,
    save_registry,
)
from trading_core.experiments.parameter_sweep import (
    ParameterSweepValidationError,
    expand_parameter_grid,
    run_parameter_sweep,
    run_parameter_sweep_from_config,
    save_sweep_json,
    save_sweep_markdown,
    validate_sweep_config,
)

__all__ = [
    "ExperimentRegistry",
    "ParameterSweepValidationError",
    "build_registry_markdown",
    "expand_parameter_grid",
    "get_experiment",
    "list_experiments",
    "load_registry",
    "register_experiment",
    "run_parameter_sweep",
    "run_parameter_sweep_from_config",
    "save_registry",
    "save_sweep_json",
    "save_sweep_markdown",
    "validate_sweep_config",
]
