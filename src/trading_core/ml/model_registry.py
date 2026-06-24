"""Optional ML model dependency checks for shadow research."""

from __future__ import annotations


LIGHTGBM_REQUIRED_MESSAGE = (
    "lightgbm is required for model-type=lightgbm. Install it manually or use model-type=mock."
)
SUPPORTED_MODEL_TYPES = {"mock", "lightgbm"}


def require_supported_model_type(model_type: str) -> None:
    if model_type not in SUPPORTED_MODEL_TYPES:
        raise ValueError(f"Unsupported model_type: {model_type}")


def require_lightgbm() -> object:
    try:
        import lightgbm  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise RuntimeError(LIGHTGBM_REQUIRED_MESSAGE) from exc
    return lightgbm
