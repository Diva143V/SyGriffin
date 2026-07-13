from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import Field

from griffin.platform.skills.models import PlatformModel

EventType = Literal[
    "run_started",
    "run_completed",
    "run_failed",
    "stage_started",
    "stage_completed",
    "stage_completed_with_warnings",
    "stage_failed",
    "stage_blocked",
    "stage_skipped",
    "stage_resumed",
    "checkpoint_written",
    "checkpoint_invalidated",
]


class RuntimeEvent(PlatformModel):
    schema_version: Literal["1.0"] = "1.0"
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: str
    recipe_id: str
    recipe_version: str
    stage_id: str | None = None
    skill_id: str | None = None
    skill_version: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class EventPublisher(Protocol):
    def publish(self, event: RuntimeEvent) -> None: ...


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    def publish(self, event: RuntimeEvent) -> None:
        self.events.append(event)


class JsonlEventPublisher:
    def __init__(self, path: Path) -> None:
        self.path = path

    def publish(self, event: RuntimeEvent) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.model_dump(mode="json"), sort_keys=True) + "\n")
