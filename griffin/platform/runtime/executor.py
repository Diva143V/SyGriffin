from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from griffin.platform.recipes.models import RecipeManifest
from griffin.platform.skills.models import (
    ProvenanceRecord,
    SkillExecutionContext,
    SkillRequest,
    StructuredFinding,
)
from griffin.platform.skills.registry import SkillRegistry

from .checkpoints import validate_checkpoint
from .events import EventPublisher, EventType, JsonlEventPublisher, RuntimeEvent
from .graph import stable_topological_order
from .hashing import hash_file, hash_value
from .models import RecipeRunResult, StageExecutionResult
from .resolver import SkillImplementationResolver
from .store import RunStore


class RecipeExecutor:
    """Deterministic synchronous executor; parallel execution is intentionally absent."""

    def __init__(self, skills: SkillRegistry, implementations: SkillImplementationResolver) -> None:
        self.skills = skills
        self.implementations = implementations

    def execute(
        self,
        recipe: RecipeManifest,
        inputs: dict[str, Any],
        config: dict[str, Any],
        run_id: str,
        run_dir: str | Path,
        resume: bool = False,
        publisher: EventPublisher | None = None,
    ) -> RecipeRunResult:
        ordered = stable_topological_order(recipe, self.skills)
        implementations = {
            stage.id: self.implementations.resolve(stage.skill, stage.skill_version)
            for stage in ordered
        }
        store = RunStore(Path(run_dir), resume)
        recipe_data = recipe.model_dump(mode="json")
        recipe_fingerprint = hash_value({"recipe": recipe_data, "inputs": inputs, "config": config})
        store.initialize(recipe_data, inputs, config)
        events = publisher or JsonlEventPublisher(store.run_dir / "events.jsonl")
        started = datetime.now(timezone.utc)
        self._event(events, "run_started", run_id, recipe)
        results: dict[str, StageExecutionResult] = {}
        blocking_failed = False
        for stage in ordered:
            dependencies = [results[item] for item in stage.depends_on]
            unusable = [
                item.stage_id
                for item in dependencies
                if item.status not in {"completed", "completed_with_warnings", "resumed"}
            ]
            fingerprint = hash_value(
                {
                    "recipe": recipe_fingerprint,
                    "stage": stage.model_dump(mode="json"),
                    "dependencies": [item.result_hash for item in dependencies],
                }
            )
            provenance = ProvenanceRecord(
                run_id=run_id, recipe_id=recipe.id, recipe_version=recipe.version
            )
            manifest = self.skills.get(stage.skill, stage.skill_version)
            checkpoint_path = store.checkpoint_path(stage.id)
            validation = (
                validate_checkpoint(
                    checkpoint_path,
                    run_dir=store.run_dir,
                    run_id=run_id,
                    recipe_id=recipe.id,
                    recipe_version=recipe.version,
                    recipe_fingerprint=recipe_fingerprint,
                    stage_id=stage.id,
                    skill_id=stage.skill,
                    skill_version=stage.skill_version,
                    stage_fingerprint=fingerprint,
                    deterministic=manifest.execution.deterministic,
                    resumable=manifest.execution.resumable,
                )
                if resume
                else None
            )
            if validation is not None and validation.valid:
                result_path = store.run_dir / validation.metadata["stage_result_path"]
                original = StageExecutionResult.model_validate_json(
                    result_path.read_text(encoding="utf-8")
                )
                result = original.model_copy(
                    update={
                        "status": "resumed",
                        "executed": False,
                        "resumed": True,
                        "checkpoint_path": str(checkpoint_path.relative_to(store.run_dir)),
                    }
                )
                self._event(events, "stage_resumed", run_id, recipe, stage)
                results[stage.id] = result
                continue
            if validation is not None and validation.reason_code not in {
                "checkpoint_missing",
                "skill_not_deterministic",
                "skill_not_resumable",
            }:
                self._event(
                    events,
                    "checkpoint_invalidated",
                    run_id,
                    recipe,
                    stage,
                    {"reason": validation.reason_code},
                )
            if unusable or blocking_failed:
                finding = StructuredFinding(
                    code="dependency_blocked",
                    severity="error",
                    message="blocked by: " + ", ".join(unusable or ["prior blocking failure"]),
                )
                result = StageExecutionResult(
                    run_id=run_id,
                    stage_id=stage.id,
                    skill_id=stage.skill,
                    skill_version=stage.skill_version,
                    status="blocked",
                    dependency_stage_ids=stage.depends_on,
                    errors=[finding],
                    provenance=provenance,
                    stage_fingerprint=fingerprint,
                    executed=False,
                    completed_at=datetime.now(timezone.utc),
                )
                self._event(
                    events, "stage_blocked", run_id, recipe, stage, {"dependencies": unusable}
                )
            else:
                self._event(events, "stage_started", run_id, recipe, stage)
                try:
                    request = SkillRequest(
                        stage_id=stage.id, parameters={"inputs": inputs, "config": config}
                    )
                    context = SkillExecutionContext(
                        run_id=run_id,
                        recipe_id=recipe.id,
                        recipe_version=recipe.version,
                        working_directory=str(store.stage_dir(stage.id)),
                    )
                    skill_result = implementations[stage.id].execute(request, context)
                    skill_result.ensure_required_outputs(
                        [item.id for item in manifest.outputs if item.required]
                    )
                    for artifact in skill_result.outputs:
                        artifact_path = store.stage_dir(stage.id) / artifact.uri
                        if not artifact_path.is_file():
                            raise ValueError(f"output artifact is missing: {artifact.uri}")
                        artifact.content_hash = hash_file(artifact_path)
                    status = skill_result.status
                    result = StageExecutionResult(
                        run_id=run_id,
                        stage_id=stage.id,
                        skill_id=stage.skill,
                        skill_version=stage.skill_version,
                        status=status,
                        dependency_stage_ids=stage.depends_on,
                        inputs=skill_result.inputs,
                        outputs=skill_result.outputs,
                        metrics=skill_result.metrics,
                        warnings=skill_result.warnings,
                        errors=skill_result.errors,
                        provenance=skill_result.provenance,
                        stage_fingerprint=fingerprint,
                        completed_at=skill_result.completed_at,
                    )
                    result.result_hash = hash_value(
                        result.model_dump(mode="json", exclude={"result_hash"})
                    )
                    store.atomic_json(
                        store.stage_dir(stage.id) / "result.json", result.model_dump(mode="json")
                    )
                    if (
                        status in {"completed", "completed_with_warnings"}
                        and manifest.execution.deterministic
                        and manifest.execution.resumable
                    ):
                        checkpoint = {
                            "schema_version": "1.0",
                            "run_id": run_id,
                            "recipe_id": recipe.id,
                            "recipe_version": recipe.version,
                            "recipe_fingerprint": recipe_fingerprint,
                            "stage_id": stage.id,
                            "skill_id": stage.skill,
                            "skill_version": stage.skill_version,
                            "stage_fingerprint": fingerprint,
                            "stage_result_path": str(Path("stages") / stage.id / "result.json"),
                            "stage_result_hash": result.result_hash,
                            "outputs": [
                                {
                                    "path": str(Path("stages") / stage.id / item.uri),
                                    "content_hash": item.content_hash,
                                }
                                for item in result.outputs
                            ],
                            "deterministic": True,
                            "resumable": True,
                        }
                        store.atomic_json(checkpoint_path, checkpoint)
                        result.checkpoint_path = str(checkpoint_path.relative_to(store.run_dir))
                        self._event(events, "checkpoint_written", run_id, recipe, stage)
                    event_type: EventType = (
                        "stage_completed_with_warnings"
                        if status == "completed_with_warnings"
                        else "stage_completed"
                    )
                    self._event(events, event_type, run_id, recipe, stage)
                    if status == "failed" and stage.blocking:
                        blocking_failed = True
                except Exception as exc:
                    finding = StructuredFinding(
                        code="stage_execution_error", severity="error", message=str(exc)
                    )
                    result = StageExecutionResult(
                        run_id=run_id,
                        stage_id=stage.id,
                        skill_id=stage.skill,
                        skill_version=stage.skill_version,
                        status="failed",
                        dependency_stage_ids=stage.depends_on,
                        errors=[finding],
                        provenance=provenance,
                        stage_fingerprint=fingerprint,
                        completed_at=datetime.now(timezone.utc),
                    )
                    result.result_hash = hash_value(
                        result.model_dump(mode="json", exclude={"result_hash"})
                    )
                    store.atomic_json(
                        store.stage_dir(stage.id) / "result.json", result.model_dump(mode="json")
                    )
                    self._event(events, "stage_failed", run_id, recipe, stage, {"error": str(exc)})
                    if stage.blocking:
                        blocking_failed = True
            results[stage.id] = result
        stage_list = list(results.values())
        status = "failed" if blocking_failed else "completed"
        if status == "completed" and any(
            item.status in {"failed", "blocked", "completed_with_warnings"} for item in stage_list
        ):
            status = "completed_with_warnings"
        run = RecipeRunResult(
            run_id=run_id,
            recipe_id=recipe.id,
            recipe_version=recipe.version,
            status=status,
            started_at=started,
            completed_at=datetime.now(timezone.utc),
            resolved_inputs=inputs,
            resolved_config=config,
            stage_results=stage_list,
            run_directory=str(store.run_dir),
            manifest_path="run_manifest.json",
            recipe_fingerprint=recipe_fingerprint,
        )
        store.atomic_json(store.run_dir / "run.json", run.model_dump(mode="json"))
        store.atomic_json(store.run_dir / "run_manifest.json", run.model_dump(mode="json"))
        self._event(events, "run_failed" if status == "failed" else "run_completed", run_id, recipe)
        return run

    @staticmethod
    def _event(
        events: EventPublisher,
        event_type: EventType,
        run_id: str,
        recipe: RecipeManifest,
        stage: Any = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        events.publish(
            RuntimeEvent(
                event_type=event_type,
                run_id=run_id,
                recipe_id=recipe.id,
                recipe_version=recipe.version,
                stage_id=None if stage is None else stage.id,
                skill_id=None if stage is None else stage.skill,
                skill_version=None if stage is None else stage.skill_version,
                payload=payload or {},
            )
        )
