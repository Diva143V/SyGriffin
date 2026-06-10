from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from griffin import __version__
from griffin.core.models import RunConfig, RunManifest, model_to_dict


def create_manifest(config: RunConfig, input_hash: str) -> RunManifest:
    return RunManifest(
        sample_id=config.sample_id,
        started_at=datetime.now(timezone.utc),
        mock_mode=config.mock_mode,
        parameters=model_to_dict(config),
        input_hashes={"vcf": input_hash},
        tool_versions={"griffin": __version__, "python": platform.python_version()},
    )


def write_manifest(path: Path, manifest: RunManifest) -> None:
    path.write_text(json.dumps(model_to_dict(manifest), indent=2, sort_keys=True), encoding="utf-8")


def load_manifest(path: Path) -> RunManifest:
    return RunManifest(**json.loads(path.read_text(encoding="utf-8")))
