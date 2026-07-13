from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field

from griffin.platform.skills.models import PlatformModel

from .errors import CheckpointValidationError
from .hashing import hash_file, hash_value


def read_checkpoint(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckpointValidationError(f"invalid checkpoint '{path}': {exc}") from exc
    if not isinstance(value, dict):
        raise CheckpointValidationError(f"invalid checkpoint '{path}': expected object")
    return value


class CheckpointValidationResult(PlatformModel):
    valid: bool
    reason_code: str | None = None
    explanation: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def validate_checkpoint(
    path: Path,
    *,
    run_dir: Path,
    run_id: str,
    recipe_id: str,
    recipe_version: str,
    recipe_fingerprint: str,
    stage_id: str,
    skill_id: str,
    skill_version: str,
    stage_fingerprint: str,
    deterministic: bool,
    resumable: bool,
) -> CheckpointValidationResult:
    if not path.exists():
        return CheckpointValidationResult(
            valid=False, reason_code="checkpoint_missing", explanation="checkpoint does not exist"
        )
    try:
        value = read_checkpoint(path)
    except CheckpointValidationError as exc:
        return CheckpointValidationResult(
            valid=False, reason_code="checkpoint_corrupt", explanation=str(exc)
        )
    expected = {
        "run_id": run_id,
        "recipe_id": recipe_id,
        "recipe_version": recipe_version,
        "recipe_fingerprint": recipe_fingerprint,
        "stage_id": stage_id,
        "skill_id": skill_id,
        "skill_version": skill_version,
        "stage_fingerprint": stage_fingerprint,
    }
    codes = {
        "run_id": "run_mismatch",
        "recipe_id": "recipe_mismatch",
        "recipe_version": "recipe_mismatch",
        "recipe_fingerprint": "recipe_fingerprint_mismatch",
        "stage_id": "stage_mismatch",
        "skill_id": "skill_mismatch",
        "skill_version": "skill_mismatch",
        "stage_fingerprint": "stage_fingerprint_mismatch",
    }
    if value.get("schema_version") != "1.0":
        return CheckpointValidationResult(
            valid=False, reason_code="schema_mismatch", explanation="unsupported checkpoint schema"
        )
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            return CheckpointValidationResult(
                valid=False, reason_code=codes[key], explanation=f"checkpoint {key} does not match"
            )
    if not deterministic:
        return CheckpointValidationResult(
            valid=False,
            reason_code="skill_not_deterministic",
            explanation="skill is not deterministic",
        )
    if not resumable:
        return CheckpointValidationResult(
            valid=False, reason_code="skill_not_resumable", explanation="skill is not resumable"
        )
    result_path = run_dir / value.get("stage_result_path", "")
    if not result_path.is_file():
        return CheckpointValidationResult(
            valid=False, reason_code="result_missing", explanation="stage result missing"
        )
    try:
        result_value = json.loads(result_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return CheckpointValidationResult(
            valid=False, reason_code="result_missing", explanation="stage result is invalid"
        )
    if result_value.get("status") not in {"completed", "completed_with_warnings"}:
        return CheckpointValidationResult(
            valid=False,
            reason_code="result_status_invalid",
            explanation="stage result is not successful",
        )
    if hash_value(
        {key: value for key, value in result_value.items() if key != "result_hash"}
    ) != value.get("stage_result_hash"):
        return CheckpointValidationResult(
            valid=False,
            reason_code="result_hash_mismatch",
            explanation="stage result hash does not match",
        )
    for artifact in value.get("outputs", []):
        artifact_path = run_dir / artifact.get("path", "")
        if not artifact_path.is_file() or run_dir.resolve() not in artifact_path.resolve().parents:
            return CheckpointValidationResult(
                valid=False,
                reason_code="artifact_path_invalid",
                explanation="artifact path is invalid",
            )
        if hash_file(artifact_path) != artifact.get("content_hash"):
            return CheckpointValidationResult(
                valid=False,
                reason_code="artifact_hash_mismatch",
                explanation="artifact hash does not match",
            )
    return CheckpointValidationResult(valid=True, metadata=value)
