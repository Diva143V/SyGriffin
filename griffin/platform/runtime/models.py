from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import Field

from griffin.platform.skills.models import (
    ArtifactReference,
    PlatformModel,
    ProvenanceRecord,
    StructuredFinding,
)

RunStatus = Literal["pending", "running", "completed", "completed_with_warnings", "failed"]
StageStatus = Literal[
    "pending",
    "running",
    "completed",
    "completed_with_warnings",
    "failed",
    "blocked",
    "skipped",
    "resumed",
]


class StageExecutionResult(PlatformModel):
    run_id: str
    stage_id: str
    skill_id: str
    skill_version: str
    status: StageStatus
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    dependency_stage_ids: list[str] = Field(default_factory=list)
    inputs: list[ArtifactReference] = Field(default_factory=list)
    outputs: list[ArtifactReference] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    warnings: list[StructuredFinding] = Field(default_factory=list)
    errors: list[StructuredFinding] = Field(default_factory=list)
    provenance: ProvenanceRecord
    checkpoint_path: str | None = None
    stage_fingerprint: str
    result_hash: str | None = None
    executed: bool = True
    resumed: bool = False


class RecipeRunResult(PlatformModel):
    run_id: str
    recipe_id: str
    recipe_version: str
    status: RunStatus
    started_at: datetime
    completed_at: datetime | None = None
    resolved_inputs: dict[str, Any] = Field(default_factory=dict)
    resolved_config: dict[str, Any] = Field(default_factory=dict)
    stage_results: list[StageExecutionResult] = Field(default_factory=list)
    warnings: list[StructuredFinding] = Field(default_factory=list)
    errors: list[StructuredFinding] = Field(default_factory=list)
    run_directory: str
    manifest_path: str
    provenance_references: list[ArtifactReference] = Field(default_factory=list)
    recipe_fingerprint: str
