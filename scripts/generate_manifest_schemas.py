"""Generate checked-in JSON Schemas for Griffin manifest contracts."""

from pathlib import Path

from griffin.platform.schema import write_manifest_schemas

if __name__ == "__main__":
    write_manifest_schemas(Path(__file__).resolve().parents[1] / "schemas")
