from __future__ import annotations

from typing import Any

from griffin.bio.peptide_generator import generate_peptides
from griffin.core.models import AnnotatedVariant, PeptideCandidate


class NeoantigenAgent:
    def __init__(self, adapter: Any = None):
        self.adapter = adapter

    def generate(
        self,
        variants: list[AnnotatedVariant],
        hla_alleles: list[str],
        lengths: list[int],
        mock_mode: bool = True,
    ) -> list[PeptideCandidate]:
        return generate_peptides(variants, hla_alleles, lengths, mock_mode=mock_mode)
