"""Deterministic JSON Schema generation for platform manifests."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from griffin.platform.recipes.models import RecipeManifest
from griffin.platform.skills.models import SkillManifest


def manifest_schema_documents() -> dict[str, str]:
    models: dict[str, type[BaseModel]] = {
        "skill-manifest.schema.json": SkillManifest,
        "recipe-manifest.schema.json": RecipeManifest,
    }
    return {
        filename: json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n"
        for filename, model in models.items()
    }


def write_manifest_schemas(directory: str | Path) -> None:
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    for filename, contents in manifest_schema_documents().items():
        (target / filename).write_text(contents, encoding="utf-8")
