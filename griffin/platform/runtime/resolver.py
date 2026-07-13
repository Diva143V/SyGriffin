from __future__ import annotations

from typing import Protocol

from griffin.platform.skills.protocol import Skill

from .errors import SkillResolutionError


class SkillImplementationResolver(Protocol):
    def resolve(self, skill_id: str, version: str) -> Skill: ...


class InMemorySkillImplementationResolver:
    def __init__(self) -> None:
        self._skills: dict[tuple[str, str], Skill] = {}

    def register(self, skill: Skill) -> None:
        key = (skill.manifest.id, skill.manifest.version)
        if key in self._skills:
            raise SkillResolutionError(f"implementation already registered for {key[0]} {key[1]}")
        self._skills[key] = skill

    def resolve(self, skill_id: str, version: str) -> Skill:
        try:
            return self._skills[(skill_id, version)]
        except KeyError as exc:
            raise SkillResolutionError(
                f"no executable implementation for skill '{skill_id}' version '{version}'"
            ) from exc
