"""Deterministic no-op skill used only to verify platform contracts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from griffin.platform.skills.loader import load_skill_manifest
from griffin.platform.skills.models import (
    ArtifactReference,
    ProvenanceRecord,
    SkillExecutionContext,
    SkillRequest,
    SkillResult,
    ValidationResult,
)


class NoOpSkill:
    manifest = load_skill_manifest(Path(__file__).with_name("skill.yaml"))

    def validate(self, request: SkillRequest) -> ValidationResult:
        return ValidationResult(valid=True)

    def execute(self, request: SkillRequest, context: SkillExecutionContext) -> SkillResult:
        now = datetime.now(timezone.utc)
        artifact = Path(context.working_directory or ".") / "artifacts" / "no-op.json"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            json.dumps(
                {
                    "message": "Griffin no-op skill completed",
                    "skill_id": "no-op",
                    "skill_version": "0.1.0",
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return SkillResult(
            skill_id=self.manifest.id,
            skill_version=self.manifest.version,
            stage_id=request.stage_id,
            status="completed",
            started_at=now,
            completed_at=now,
            outputs=[ArtifactReference(id="no-op-artifact", uri="artifacts/no-op.json")],
            provenance=ProvenanceRecord(
                run_id=context.run_id,
                recipe_id=context.recipe_id,
                recipe_version=context.recipe_version,
            ),
        )
