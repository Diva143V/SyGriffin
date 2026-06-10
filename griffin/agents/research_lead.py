from __future__ import annotations

from griffin.core.models import FinalCandidate, ScoredCandidate, model_copy, model_to_dict


class ResearchLeadAgent:
    def review(self, candidates: list[ScoredCandidate]) -> list[FinalCandidate]:
        final: list[FinalCandidate] = []
        for rank, candidate in enumerate(candidates, start=1):
            label = self._label(candidate)
            limitations = [
                "Computational prediction only.",
                "Requires wet-lab validation and expert review.",
            ]
            final.append(
                FinalCandidate(
                    **model_to_dict(
                        model_copy(
                            candidate,
                            update={
                                "confidence_label": label,
                                "rationale": self._rationale(candidate, label),
                            },
                        )
                    ),
                    rank=rank,
                    limitations=limitations,
                )
            )
        return final

    def _label(self, candidate: ScoredCandidate) -> str:
        if candidate.binding_score >= 0.65 and candidate.composite_score >= 0.75:
            return "high_research_priority"
        if candidate.binding_score >= 0.35 and candidate.composite_score >= 0.55:
            return "medium_research_priority"
        if candidate.binding_score >= 0.35:
            return "low_research_priority"
        return "insufficient_evidence"

    def _rationale(self, candidate: ScoredCandidate, label: str) -> str:
        return (
            f"{candidate.gene} {candidate.protein_change or ''} is ranked as {label} based on "
            f"binding score {candidate.binding_score:.2f}, presentation "
            f"{candidate.presentation_score:.2f}, mutation impact "
            f"{candidate.mutation_impact_score:.2f}, and evidence {candidate.evidence_score:.2f}."
        )
