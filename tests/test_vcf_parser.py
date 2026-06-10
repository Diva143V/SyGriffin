from pathlib import Path

import pytest

from griffin.bio.vcf_parser import parse_vcf
from griffin.core.exceptions import InvalidVCFError


def test_vcf_parser_reads_fixture(fixture_dir: Path):
    variants = parse_vcf(fixture_dir / "tiny.vcf")
    assert variants[0].variant_id == "chr7:140453136:A:T"
    assert variants[0].info["GENE"] == "BRAF"


def test_invalid_vcf_fails_clearly(tmp_path: Path):
    path = tmp_path / "bad.vcf"
    path.write_text("7\t140453136\t.\tA\tT\t60\tPASS\t.\n", encoding="utf-8")
    with pytest.raises(InvalidVCFError, match="missing #CHROM header"):
        parse_vcf(path)
