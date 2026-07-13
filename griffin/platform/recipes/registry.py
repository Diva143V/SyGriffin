"""In-memory, exact-version registry for recipe manifests."""

from __future__ import annotations

import semver

from .models import RecipeManifest


class RecipeRegistryError(ValueError):
    """Raised for invalid recipe registry operations."""


class RecipeRegistry:
    def __init__(self) -> None:
        self._manifests: dict[tuple[str, str], RecipeManifest] = {}

    def register(self, manifest: RecipeManifest) -> None:
        key = (manifest.id, manifest.version)
        if key in self._manifests:
            raise RecipeRegistryError(
                f"recipe '{manifest.id}' version '{manifest.version}' is already registered"
            )
        self._manifests[key] = manifest

    def get(self, recipe_id: str, version: str) -> RecipeManifest:
        key = (recipe_id, version)
        if key in self._manifests:
            return self._manifests[key]
        if not any(registered_id == recipe_id for registered_id, _ in self._manifests):
            raise RecipeRegistryError(f"unknown recipe id '{recipe_id}'")
        raise RecipeRegistryError(f"unknown version '{version}' for recipe '{recipe_id}'")

    def list_versions(self, recipe_id: str) -> list[RecipeManifest]:
        versions = [
            manifest
            for (registered_id, _), manifest in self._manifests.items()
            if registered_id == recipe_id
        ]
        if not versions:
            raise RecipeRegistryError(f"unknown recipe id '{recipe_id}'")
        return sorted(versions, key=lambda manifest: semver.Version.parse(manifest.version))

    def list_all(self) -> list[RecipeManifest]:
        return sorted(
            self._manifests.values(),
            key=lambda manifest: (manifest.id, semver.Version.parse(manifest.version)),
        )
