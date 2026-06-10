from __future__ import annotations

from pathlib import Path


class JsonCache:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def key_path(self, key: str) -> Path:
        return self.directory / f"{key}.json"
