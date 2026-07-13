"""Safe, non-executing YAML loader for recipe manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import ValidationError

from .models import RecipeManifest


class RecipeManifestLoadError(ValueError):
    """A recipe manifest could not be read or validated."""


def load_recipe_manifest(path: str | Path) -> RecipeManifest:
    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise RecipeManifestLoadError(f"recipe manifest file does not exist: {manifest_path}")
    try:
        data: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RecipeManifestLoadError(
            f"failed to read recipe manifest '{manifest_path}': {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise RecipeManifestLoadError(
            f"recipe manifest '{manifest_path}' must contain a YAML mapping"
        )
    try:
        return RecipeManifest.model_validate(data)
    except ValidationError as exc:
        raise RecipeManifestLoadError(f"invalid recipe manifest '{manifest_path}': {exc}") from exc
