from __future__ import annotations

from griffin.platform.recipes.models import RecipeManifest, RecipeStage
from griffin.platform.skills.registry import SkillRegistry

from .errors import RecipeCycleError, UnknownStageDependencyError


def stable_topological_order(recipe: RecipeManifest, skills: SkillRegistry) -> list[RecipeStage]:
    stages = {stage.id: stage for stage in recipe.stages}
    order = [stage.id for stage in recipe.stages]
    for stage in recipe.stages:
        skills.get(stage.skill, stage.skill_version)
        for dependency in stage.depends_on:
            if dependency not in stages:
                message = (
                    f"recipe '{recipe.id}' stage '{stage.id}' depends on unknown "
                    f"stage '{dependency}'"
                )
                raise UnknownStageDependencyError(message)
            if dependency == stage.id:
                raise UnknownStageDependencyError(
                    f"recipe '{recipe.id}' stage '{stage.id}' cannot depend on itself"
                )
    pending = {stage.id: set(stage.depends_on) for stage in recipe.stages}
    result: list[RecipeStage] = []
    while pending:
        ready = [stage_id for stage_id in order if stage_id in pending and not pending[stage_id]]
        if not ready:
            raise RecipeCycleError(f"recipe '{recipe.id}' contains a dependency cycle")
        for stage_id in ready:
            result.append(stages[stage_id])
            del pending[stage_id]
        for dependencies in pending.values():
            dependencies.difference_update(ready)
    return result
