from pathlib import Path

from griffin.platform.runtime.hashing import hash_file, hash_value


def test_hashing_is_canonical_and_hashes_files(tmp_path: Path) -> None:
    assert hash_value({"a": 1, "b": 2}) == hash_value({"b": 2, "a": 1})
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"griffin")
    assert len(hash_file(artifact)) == 64
