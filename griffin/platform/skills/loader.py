"""Safe, non-executing YAML loader for skill manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import ValidationError

from .models import SkillManifest


class SkillManifestLoadError(ValueError):
    """A skill manifest could not be read or validated."""


def load_skill_manifest(path: str | Path) -> SkillManifest:
    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise SkillManifestLoadError(f"skill manifest file does not exist: {manifest_path}")
    try:
        data: Any = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SkillManifestLoadError(
            f"failed to read skill manifest '{manifest_path}': {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SkillManifestLoadError(
            f"skill manifest '{manifest_path}' must contain a YAML mapping"
        )
    try:
        return SkillManifest.model_validate(data)
    except ValidationError as exc:
        raise SkillManifestLoadError(f"invalid skill manifest '{manifest_path}': {exc}") from exc
