"""Protocol for independently callable Griffin skills."""

from __future__ import annotations

from typing import Protocol

from .models import (
    SkillExecutionContext,
    SkillManifest,
    SkillRequest,
    SkillResult,
    ValidationResult,
)


class Skill(Protocol):
    manifest: SkillManifest

    def validate(self, request: SkillRequest) -> ValidationResult:
        """Validate an invocation without executing it."""

    def execute(self, request: SkillRequest, context: SkillExecutionContext) -> SkillResult:
        """Execute the skill. Generic orchestration is introduced in Milestone 2."""
