from __future__ import annotations

from griffin.core.exceptions import GriffinError
from griffin.core.hashing import stable_hash
from griffin.core.models import AnnotatedVariant, PeptideCandidate

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"


def _deterministic_peptide(seed: str, length: int) -> str:
    digest = stable_hash(seed)
    chars = []
    for idx in range(length):
        chars.append(AMINO_ACIDS[int(digest[idx * 2 : idx * 2 + 2], 16) % len(AMINO_ACIDS)])
    return "".join(chars)


def generate_peptides(
    variants: list[AnnotatedVariant],
    hla_alleles: list[str],
    lengths: list[int],
    mock_mode: bool = True,
) -> list[PeptideCandidate]:
    if not mock_mode:
        raise GriffinError(
            "Biologically traceable peptide generation is not implemented yet. Griffin will not "
            "fabricate peptide sequences in non-mock mode; rerun with --mock for demos."
        )
    candidates: list[PeptideCandidate] = []
    counter = 1
    for variant in variants:
        for hla in hla_alleles:
            for length in lengths:
                peptide = _deterministic_peptide(f"{variant.variant_id}:{hla}:{length}", length)
                presentation = min(1.0, 0.35 + (variant.impact_score * 0.55) + (length == 9) * 0.05)
                candidates.append(
                    PeptideCandidate(
                        candidate_id=f"cand_{counter:04d}",
                        variant_id=variant.variant_id,
                        source_variant_id=variant.variant_id,
                        chromosome=variant.chrom,
                        position=variant.pos,
                        ref=variant.ref,
                        alt=variant.alt,
                        gene=variant.gene,
                        transcript=variant.transcript,
                        mutation=variant.protein_change,
                        protein_change=variant.protein_change,
                        hla=hla,
                        peptide=peptide,
                        peptide_length=length,
                        mutation_position_in_peptide=min(length, max(1, (length + 1) // 2)),
                        presentation_score=round(presentation, 3),
                        mutation_impact_score=variant.impact_score,
                        is_mock=True,
                        annotation_source=variant.annotation_source,
                        sequence_context_source="mock",
                    )
                )
                counter += 1
    return candidates
