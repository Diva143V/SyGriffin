from __future__ import annotations

import json
from pathlib import Path

from griffin.platform.recipes.loader import load_recipe_manifest
from griffin.platform.runtime.executor import RecipeExecutor
from griffin.platform.runtime.resolver import InMemorySkillImplementationResolver
from griffin.platform.skills.loader import load_skill_manifest
from griffin.platform.skills.registry import SkillRegistry
from griffin.skills.noop import NoOpSkill

ROOT = Path(__file__).parents[3]


class CountingNoOp(NoOpSkill):
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request, context):  # type: ignore[no-untyped-def]
        self.calls += 1
        return super().execute(request, context)


def test_noop_runtime_checkpoint_and_resume(tmp_path: Path) -> None:
    manifest = load_skill_manifest(ROOT / "griffin/skills/noop/skill.yaml")
    recipe = load_recipe_manifest(ROOT / "griffin/recipes/noop/recipe.yaml")
    registry = SkillRegistry()
    registry.register(manifest)
    skill = CountingNoOp()
    resolver = InMemorySkillImplementationResolver()
    resolver.register(skill)
    executor = RecipeExecutor(registry, resolver)

    first = executor.execute(recipe, {}, {}, "run-1", tmp_path / "run-1")
    resumed = executor.execute(recipe, {}, {}, "run-1", tmp_path / "run-1", resume=True)

    assert first.status == "completed"
    assert first.stage_results[0].status == "completed"
    assert resumed.stage_results[0].status == "resumed"
    assert resumed.stage_results[0].executed is False
    assert skill.calls == 1
    artifact = tmp_path / "run-1/stages/no-op-stage/artifacts/no-op.json"
    assert json.loads(artifact.read_text(encoding="utf-8"))["skill_id"] == "no-op"
    assert (tmp_path / "run-1/checkpoints/no-op-stage.json").is_file()
