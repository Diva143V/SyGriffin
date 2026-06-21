"""In-memory, exact-version registry for skill manifests."""

from __future__ import annotations

import semver

from .models import SkillManifest


class SkillRegistryError(ValueError):
    """Raised for invalid skill registry operations."""


class SkillRegistry:
    def __init__(self) -> None:
        self._manifests: dict[tuple[str, str], SkillManifest] = {}

    def register(self, manifest: SkillManifest) -> None:
        key = (manifest.id, manifest.version)
        if key in self._manifests:
            raise SkillRegistryError(
                f"skill '{manifest.id}' version '{manifest.version}' is already registered"
            )
        self._manifests[key] = manifest

    def get(self, skill_id: str, version: str) -> SkillManifest:
        key = (skill_id, version)
        if key in self._manifests:
            return self._manifests[key]
        if not any(registered_id == skill_id for registered_id, _ in self._manifests):
            raise SkillRegistryError(f"unknown skill id '{skill_id}'")
        raise SkillRegistryError(f"unknown version '{version}' for skill '{skill_id}'")

    def list_versions(self, skill_id: str) -> list[SkillManifest]:
        versions = [
            manifest
            for (registered_id, _), manifest in self._manifests.items()
            if registered_id == skill_id
        ]
        if not versions:
            raise SkillRegistryError(f"unknown skill id '{skill_id}'")
        return sorted(versions, key=lambda manifest: semver.Version.parse(manifest.version))

    def list_all(self) -> list[SkillManifest]:
        return sorted(
            self._manifests.values(),
            key=lambda manifest: (manifest.id, semver.Version.parse(manifest.version)),
        )
