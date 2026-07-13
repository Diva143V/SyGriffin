from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class RunStore:
    def __init__(self, run_dir: Path, resume: bool) -> None:
        self.run_dir = run_dir
        if run_dir.exists() and not resume:
            raise FileExistsError(f"run directory already exists: {run_dir}")
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "stages").mkdir(exist_ok=True)
        (run_dir / "checkpoints").mkdir(exist_ok=True)

    def atomic_json(self, path: Path, value: Any) -> None:
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True, default=str), encoding="utf-8"
        )
        os.replace(temporary, path)

    def initialize(
        self, recipe: dict[str, Any], inputs: dict[str, Any], config: dict[str, Any]
    ) -> None:
        self.atomic_json(self.run_dir / "resolved_inputs.json", inputs)
        self.atomic_json(self.run_dir / "resolved_config.json", config)
        (self.run_dir / "resolved_recipe.yaml").write_text(
            yaml.safe_dump(recipe, sort_keys=True), encoding="utf-8"
        )

    def stage_dir(self, stage_id: str) -> Path:
        directory = self.run_dir / "stages" / stage_id
        (directory / "artifacts").mkdir(parents=True, exist_ok=True)
        return directory

    def checkpoint_path(self, stage_id: str) -> Path:
        return self.run_dir / "checkpoints" / f"{stage_id}.json"
