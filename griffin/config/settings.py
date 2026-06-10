from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel


class Settings(BaseModel):
    cache_dir: Path = Path(".griffin/cache")
    log_level: str = "INFO"
    mock_mode: bool = False
    top_n_evidence: int = 20
    peptide_lengths: list[int] = [9, 10, 11]
    use_llm: bool = False
    llm_provider: str = "none"
    ollama_model: str = "phi3"
    ncbi_email: str | None = None
    ncbi_api_key: str | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings(
    project_dir: Path = Path("."),
    cli_overrides: dict[str, Any] | None = None,
) -> Settings:
    defaults = _load_yaml(Path(__file__).with_name("defaults.yaml"))
    config = _load_yaml(project_dir / ".griffin" / "config.yaml")
    merged: dict[str, Any] = {**defaults, **config}
    merged.update(
        {
            "cache_dir": os.getenv("GRIFFIN_CACHE_DIR", merged.get("cache_dir")),
            "log_level": os.getenv("GRIFFIN_LOG_LEVEL", merged.get("log_level")),
            "mock_mode": _as_bool(
                os.getenv("GRIFFIN_MOCK_MODE"),
                bool(merged.get("mock_mode", False)),
            ),
            "llm_provider": os.getenv("GRIFFIN_LLM_PROVIDER", merged.get("llm_provider")),
            "ollama_model": os.getenv("GRIFFIN_OLLAMA_MODEL", merged.get("ollama_model")),
            "ncbi_email": os.getenv("NCBI_EMAIL"),
            "ncbi_api_key": os.getenv("NCBI_API_KEY"),
        }
    )
    if cli_overrides:
        merged.update({k: v for k, v in cli_overrides.items() if v is not None})
    return Settings(**merged)


def ensure_project(project_dir: Path) -> None:
    for path in [
        project_dir / ".griffin" / "cache",
        project_dir / ".griffin" / "logs",
        project_dir / "runs",
        project_dir / "data" / "examples",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def write_default_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    defaults = _load_yaml(Path(__file__).with_name("defaults.yaml"))
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(defaults, handle, sort_keys=False)
