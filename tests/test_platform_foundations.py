from __future__ import annotations

from pathlib import Path

import pytest

from griffin.platform.recipes.loader import RecipeManifestLoadError, load_recipe_manifest
from griffin.platform.recipes.registry import RecipeRegistry, RecipeRegistryError
from griffin.platform.recipes.validator import (
    RecipeValidationError,
    validate_recipe_skill_references,
)
from griffin.platform.schema import manifest_schema_documents
from griffin.platform.skills.loader import SkillManifestLoadError, load_skill_manifest
from griffin.platform.skills.registry import SkillRegistry, SkillRegistryError

ROOT = Path(__file__).parents[1]
SKILL_PATH = ROOT / "griffin" / "skills" / "noop" / "skill.yaml"
RECIPE_PATH = ROOT / "griffin" / "recipes" / "noop" / "recipe.yaml"


def test_noop_manifests_load_and_resolve() -> None:
    skill = load_skill_manifest(SKILL_PATH)
    recipe = load_recipe_manifest(RECIPE_PATH)
    skills = SkillRegistry()
    skills.register(skill)
    validate_recipe_skill_references(recipe, skills)
    assert skills.get("no-op", "0.1.0") == skill


@pytest.mark.parametrize("field,value", [("id", "No_Op"), ("version", "0.1")])
def test_invalid_skill_identifier_or_version_fails(tmp_path: Path, field: str, value: str) -> None:
    original = f"{field}: no-op" if field == "id" else "version: 0.1.0"
    contents = SKILL_PATH.read_text(encoding="utf-8").replace(original, f"{field}: {value}")
    path = tmp_path / "invalid.yaml"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(SkillManifestLoadError):
        load_skill_manifest(path)


def test_safe_loader_rejects_unsafe_and_missing_yaml(tmp_path: Path) -> None:
    unsafe = tmp_path / "unsafe.yaml"
    unsafe.write_text("!!python/object/apply:os.system ['echo unsafe']", encoding="utf-8")
    with pytest.raises(SkillManifestLoadError):
        load_skill_manifest(unsafe)
    with pytest.raises(SkillManifestLoadError):
        load_skill_manifest(tmp_path / "missing.yaml")


def test_recipe_duplicate_stage_and_missing_skill_fail(tmp_path: Path) -> None:
    duplicate_stage = "\n  - id: no-op-stage\n    skill: no-op\n    skill_version: 0.1.0\n"
    duplicate = RECIPE_PATH.read_text(encoding="utf-8") + duplicate_stage
    path = tmp_path / "duplicate.yaml"
    path.write_text(duplicate, encoding="utf-8")
    with pytest.raises(RecipeManifestLoadError):
        load_recipe_manifest(path)
    recipe = load_recipe_manifest(RECIPE_PATH)
    with pytest.raises(RecipeValidationError, match="unavailable skill"):
        validate_recipe_skill_references(recipe, SkillRegistry())


def test_registries_are_exact_versioned_and_stably_sorted() -> None:
    skill = load_skill_manifest(SKILL_PATH)
    recipe = load_recipe_manifest(RECIPE_PATH)
    skills = SkillRegistry()
    skills.register(skill)
    with pytest.raises(SkillRegistryError, match="already registered"):
        skills.register(skill)
    with pytest.raises(SkillRegistryError, match="unknown version"):
        skills.get("no-op", "9.9.9")
    recipes = RecipeRegistry()
    recipes.register(recipe)
    with pytest.raises(RecipeRegistryError, match="already registered"):
        recipes.register(recipe)
    assert [item.id for item in skills.list_all()] == ["no-op"]
    assert [item.id for item in recipes.list_all()] == ["no-op-recipe"]


def test_checked_in_schemas_match_deterministic_generation() -> None:
    for filename, expected in manifest_schema_documents().items():
        assert (ROOT / "schemas" / filename).read_text(encoding="utf-8") == expected
