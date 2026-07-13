"""Typed, recipe-neutral contracts for versioned Griffin recipes."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator

from griffin.platform.skills.models import (
    _IDENTIFIER_PATTERN,
    InputDeclaration,
    OutputDeclaration,
    PlatformModel,
    VersionedModel,
)


class RecipeStage(PlatformModel):
    id: str = Field(pattern=_IDENTIFIER_PATTERN)
    skill: str = Field(pattern=_IDENTIFIER_PATTERN)
    skill_version: str
    depends_on: list[str] = Field(default_factory=list)
    blocking: bool = True
    optional: bool = False
    requires_approval: bool = False

    @model_validator(mode="after")
    def validate_stage(self) -> RecipeStage:
        VersionedModel.validate_semantic_version(self.skill_version)
        if self.id in self.depends_on:
            raise ValueError("a stage cannot depend on itself")
        return self


class RecipeManifest(VersionedModel):
    schema_version: Literal["1.0"]
    id: str = Field(pattern=_IDENTIFIER_PATTERN)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    research_use_only: bool
    inputs: list[InputDeclaration] = Field(default_factory=list)
    stages: list[RecipeStage] = Field(min_length=1)
    outputs: list[OutputDeclaration] = Field(default_factory=list)
    policies: dict[str, Any] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_stage_ids(self) -> RecipeManifest:
        stage_ids = [stage.id for stage in self.stages]
        duplicates = sorted({stage_id for stage_id in stage_ids if stage_ids.count(stage_id) > 1})
        if duplicates:
            raise ValueError("duplicate stage ids: " + ", ".join(duplicates))
        return self
