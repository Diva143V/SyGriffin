from __future__ import annotations

from pathlib import Path


class RunStore:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir

    def exists(self) -> bool:
        return self.run_dir.exists()
