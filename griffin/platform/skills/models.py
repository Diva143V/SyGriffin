"""Typed, recipe-neutral contracts for versioned Griffin skills."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

import semver
from pydantic import BaseModel, ConfigDict, Field, field_validator

_IDENTIFIER_PATTERN = r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"


class PlatformModel(BaseModel):
    """Base model that rejects unrecognised manifest fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class IdentifierModel(PlatformModel):
    """A stable lowercase kebab-case identifier."""

    id: str = Field(pattern=_IDENTIFIER_PATTERN)


class VersionedModel(PlatformModel):
    """A strict Semantic Version value represented as a string."""

    version: str

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, value: str) -> str:
        try:
            parsed = semver.Version.parse(value)
        except ValueError as exc:
            raise ValueError("must be a Semantic Version, for example '0.1.0'") from exc
        if str(parsed) != value:
            raise ValueError("must use normalized Semantic Version syntax")
        return value


class ArtifactDeclaration(IdentifierModel):
    """A generic declared input or output artifact."""

    type: str = Field(min_length=1)
    description: str = ""
    format: str | None = None


class InputDeclaration(ArtifactDeclaration):
    required: bool = True
    default: Any | None = None


class OutputDeclaration(ArtifactDeclaration):
    required: bool = True


class ExecutionContract(PlatformModel):
    runtime: Literal["python", "container", "command"]
    entrypoint: str = Field(min_length=1)
    network_access: Literal["none", "read_only", "unrestricted"] = "none"
    resumable: bool = False
    deterministic: bool = False


class PermissionDeclaration(PlatformModel):
    filesystem_read: list[str] = Field(default_factory=list)
    filesystem_write: list[str] = Field(default_factory=list)
    environment_variables: list[str] = Field(default_factory=list)


class ValidationDeclaration(IdentifierModel):
    description: str = Field(min_length=1)
    blocking: bool = True


class ProvenanceRequirements(PlatformModel):
    record_input_hashes: bool = True
    record_environment: bool = True
    record_tool_version: bool = True
    required_fields: list[str] = Field(default_factory=list)


class MockPolicy(PlatformModel):
    allowed: bool = False
    explicit_only: bool = True
    behavior_description: str = "Mock execution is not supported."


class FailurePolicy(PlatformModel):
    on_validation_error: Literal["fail"] = "fail"
    on_execution_error: Literal["fail", "warn", "skip"] = "fail"


class SkillManifest(VersionedModel):
    """A versioned, independently callable scientific capability."""

    schema_version: Literal["1.0"]
    id: str = Field(pattern=_IDENTIFIER_PATTERN)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    research_use_only: bool
    inputs: list[InputDeclaration] = Field(default_factory=list)
    outputs: list[OutputDeclaration] = Field(default_factory=list)
    execution: ExecutionContract
    permissions: PermissionDeclaration
    validations: list[ValidationDeclaration] = Field(default_factory=list)
    provenance: ProvenanceRequirements = Field(default_factory=ProvenanceRequirements)
    limitations: list[str] = Field(min_length=1)
    mock_policy: MockPolicy = Field(default_factory=MockPolicy)
    failure_policy: FailurePolicy = Field(default_factory=FailurePolicy)


class ArtifactReference(IdentifierModel):
    uri: str = Field(min_length=1)
    content_hash: str | None = None
    media_type: str | None = None


class StructuredFinding(PlatformModel):
    code: str = Field(min_length=1)
    severity: Literal["info", "warning", "error"]
    message: str = Field(min_length=1)
    details: dict[str, Any] = Field(default_factory=dict)


class ProvenanceRecord(PlatformModel):
    run_id: str = Field(min_length=1)
    recipe_id: str | None = None
    recipe_version: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)
    tool_versions: dict[str, str] = Field(default_factory=dict)
    source_artifacts: list[ArtifactReference] = Field(default_factory=list)


class SkillRequest(PlatformModel):
    stage_id: str = Field(pattern=_IDENTIFIER_PATTERN)
    inputs: list[ArtifactReference] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)


class SkillExecutionContext(PlatformModel):
    run_id: str = Field(min_length=1)
    recipe_id: str | None = None
    recipe_version: str | None = None
    required_output_ids: list[str] = Field(default_factory=list)
    working_directory: str | None = None


class ValidationResult(PlatformModel):
    valid: bool
    findings: list[StructuredFinding] = Field(default_factory=list)


class SkillResult(PlatformModel):
    skill_id: str = Field(pattern=_IDENTIFIER_PATTERN)
    skill_version: str
    stage_id: str = Field(pattern=_IDENTIFIER_PATTERN)
    status: Literal["completed", "completed_with_warnings", "failed", "skipped"]
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    inputs: list[ArtifactReference] = Field(default_factory=list)
    outputs: list[ArtifactReference] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    warnings: list[StructuredFinding] = Field(default_factory=list)
    errors: list[StructuredFinding] = Field(default_factory=list)
    provenance: ProvenanceRecord

    @field_validator("skill_version")
    @classmethod
    def validate_result_version(cls, value: str) -> str:
        return VersionedModel.validate_semantic_version(value)

    def ensure_required_outputs(self, required_output_ids: list[str]) -> None:
        """Raise when a completed result omits an output required by its stage."""

        if self.status not in {"completed", "completed_with_warnings"}:
            return
        emitted = {artifact.id for artifact in self.outputs}
        missing = sorted(set(required_output_ids) - emitted)
        if missing:
            raise ValueError(
                f"successful skill result for stage '{self.stage_id}' is missing required outputs: "
                + ", ".join(missing)
            )
