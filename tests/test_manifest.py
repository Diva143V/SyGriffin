from pathlib import Path

from griffin.core.hashing import sha256_file
from griffin.core.manifest import create_manifest
from griffin.core.models import RunConfig


def test_manifest_includes_input_hash(fixture_dir: Path, tmp_path: Path):
    vcf = fixture_dir / "tiny.vcf"
    config = RunConfig(
        sample_id="demo",
        vcf_path=vcf,
        hla_alleles=["HLA-A*02:01"],
        cancer_type="melanoma",
        output_dir=tmp_path / "run",
        mock_mode=True,
    )
    manifest = create_manifest(config, sha256_file(vcf))
    assert manifest.input_hashes["vcf"]
    assert manifest.mock_mode is True
