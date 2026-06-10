from __future__ import annotations

from pathlib import Path


class CheckpointStore:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)

    def path(self, name: str) -> Path:
        return self.directory / f"{name}.done"

    def is_done(self, name: str) -> bool:
        return self.path(name).exists()

    def mark_done(self, name: str) -> None:
        self.path(name).write_text("done\n", encoding="utf-8")

    def completed(self) -> list[str]:
        return sorted(path.stem for path in self.directory.glob("*.done"))
