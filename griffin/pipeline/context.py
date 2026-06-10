from __future__ import annotations

from pathlib import Path

from griffin.core.models import RunConfig, RunManifest


class PipelineContext:
    def __init__(self, config: RunConfig, manifest: RunManifest):
        self.config = config
        self.manifest = manifest
        self.output_dir = config.output_dir
        self.inputs_dir = self.output_dir / "inputs"
        self.logs_dir = self.output_dir / "logs"
        self.artifacts_dir = self.output_dir / "artifacts"
        self.outputs_dir = self.output_dir / "outputs"
        self.checkpoints_dir = self.output_dir / "checkpoints"

    def ensure_dirs(self) -> None:
        for path in [
            self.output_dir,
            self.inputs_dir,
            self.logs_dir,
            self.artifacts_dir,
            self.outputs_dir,
            self.checkpoints_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def artifact(self, name: str) -> Path:
        return self.artifacts_dir / name
