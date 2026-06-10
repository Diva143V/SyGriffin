from __future__ import annotations

import re

from griffin.core.exceptions import InvalidHLAError

HLA_PATTERN = re.compile(r"^HLA-[A-Z0-9]+\*\d{2}:\d{2,3}$")


def validate_hla_allele(allele: str) -> str:
    if not HLA_PATTERN.match(allele):
        raise InvalidHLAError(f"Invalid HLA allele: {allele}. Expected format like HLA-A*02:01.")
    return allele


def validate_hla_alleles(alleles: list[str]) -> list[str]:
    if not alleles:
        raise InvalidHLAError("At least one HLA allele is required.")
    return [validate_hla_allele(allele) for allele in alleles]
