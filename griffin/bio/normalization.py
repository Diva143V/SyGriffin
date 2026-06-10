from __future__ import annotations

from griffin.core.models import VariantRecord


def normalize_variant(variant: VariantRecord) -> VariantRecord:
    return variant.copy(update={"chrom": variant.chrom.removeprefix("chr")})
