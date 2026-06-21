"""Cross-manifest validation without recipe execution."""

from __future__ import annotations

from griffin.platform.skills.registry import SkillRegistry, SkillRegistryError

from .models import RecipeManifest


class RecipeValidationError(ValueError):
    """A recipe cannot be resolved against the available skill contracts."""


def validate_recipe_skill_references(recipe: RecipeManifest, skills: SkillRegistry) -> None:
    """Ensure every stage names a registered skill at an exact version."""

    for stage in recipe.stages:
        try:
            skills.get(stage.skill, stage.skill_version)
        except SkillRegistryError as exc:
            raise RecipeValidationError(
                f"recipe '{recipe.id}' stage '{stage.id}' references unavailable skill "
                f"'{stage.skill}' version '{stage.skill_version}': {exc}"
            ) from exc
