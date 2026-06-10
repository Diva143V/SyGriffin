from __future__ import annotations

from griffin.bio.peptide_generator import generate_peptides
from griffin.core.models import AnnotatedVariant, PeptideCandidate
from griffin.integrations.mhcflurry_adapter import MHCflurryAdapter


class NeoantigenAgent:
    def __init__(self, adapter: MHCflurryAdapter):
        self.adapter = adapter

    def generate(
        self, variants: list[AnnotatedVariant], hla_alleles: list[str], lengths: list[int]
    ) -> list[PeptideCandidate]:
        return generate_peptides(variants, hla_alleles, lengths)
