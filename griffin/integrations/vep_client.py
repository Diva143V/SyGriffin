from __future__ import annotations

from griffin.core.exceptions import GriffinError
from griffin.core.models import AnnotatedVariant, VariantRecord, model_to_dict


class VEPClient:
    def __init__(self, mock: bool = True):
        self.mock = mock

    def annotate_variants(self, variants: list[VariantRecord]) -> list[AnnotatedVariant]:
        if not self.mock:
            raise GriffinError(
                "Real Ensembl VEP REST annotation is not implemented yet. Griffin will not "
                "fabricate variant annotations in non-mock mode; rerun with --mock for demos."
            )
        return [self._mock_annotation(variant) for variant in variants]

    def _mock_annotation(self, variant: VariantRecord) -> AnnotatedVariant:
        gene = variant.info.get("GENE") or (
            "BRAF" if variant.chrom == "7" else "GENE" + variant.chrom
        )
        protein_change = variant.info.get("AA") or ("V600E" if gene == "BRAF" else "p.X1Y")
        impact = variant.info.get("IMPACT") or ("HIGH" if gene == "BRAF" else "MODERATE")
        impact_score = {"HIGH": 0.91, "MODERATE": 0.62, "LOW": 0.25}.get(impact, 0.1)
        return AnnotatedVariant(
            **model_to_dict(variant),
            gene=gene,
            transcript=variant.info.get("TRANSCRIPT", "ENSTMOCK000001"),
            protein_change=protein_change,
            amino_acids=protein_change,
            consequence=variant.info.get("CSQ", "missense_variant"),
            impact=impact,
            impact_score=impact_score,
            annotation_source="mock",
            raw_output={"source": "mock", "variant_id": variant.variant_id},
        )
