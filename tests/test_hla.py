import pytest

from griffin.bio.hla import validate_hla_allele
from griffin.core.exceptions import InvalidHLAError


def test_valid_hla_accepts_expected_format():
    assert validate_hla_allele("HLA-A*02:01") == "HLA-A*02:01"


def test_invalid_hla_rejects_missing_star():
    with pytest.raises(InvalidHLAError, match="Expected format"):
        validate_hla_allele("HLA-A02:01")
