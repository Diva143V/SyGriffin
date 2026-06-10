from __future__ import annotations

from griffin.core.models import (
    EvidenceRecord,
    MHCPrediction,
    PeptideCandidate,
    ScoredCandidate,
    model_to_dict,
)


def binding_score_from_ic50(ic50_nm: float) -> float:
    if ic50_nm <= 50:
        return 1.0
    if ic50_nm <= 150:
        return 0.85
    if ic50_nm <= 500:
        return 0.65
    if ic50_nm <= 1000:
        return 0.35
    return 0.10


def binding_strength(ic50_nm: float) -> str:
    if ic50_nm <= 150:
        return "strong"
    if ic50_nm <= 500:
        return "moderate"
    if ic50_nm <= 1000:
        return "weak"
    return "very_weak"


def evidence_level_score(level: str) -> float:
    return {
        "direct_neoantigen_evidence": 0.9,
        "mutation_cancer_evidence": 0.65,
        "gene_pathway_evidence": 0.45,
        "trial_context": 0.35,
        "weak_or_no_evidence": 0.0,
    }.get(level, 0.0)


def composite_score(
    binding_score: float,
    presentation_score: float,
    mutation_impact_score: float,
    evidence_score: float,
) -> float:
    score = (
        0.35 * binding_score
        + 0.25 * presentation_score
        + 0.25 * evidence_score
        + 0.15 * mutation_impact_score
    )
    if binding_score < 0.35:
        score = min(score, 0.50)
    return round(score, 4)


def score_candidates(
    candidates: list[PeptideCandidate],
    predictions: list[MHCPrediction],
    evidence: list[EvidenceRecord],
) -> list[ScoredCandidate]:
    pred_by_id = {pred.candidate_id: pred for pred in predictions}
    evidence_by_id = {record.candidate_id: record for record in evidence}
    scored: list[ScoredCandidate] = []
    for candidate in candidates:
        pred = pred_by_id[candidate.candidate_id]
        ev = evidence_by_id.get(candidate.candidate_id)
        evidence_score = ev.evidence_score if ev else 0.0
        total = composite_score(
            pred.binding_score,
            candidate.presentation_score,
            candidate.mutation_impact_score,
            evidence_score,
        )
        scored.append(
            ScoredCandidate(
                **model_to_dict(candidate),
                ic50_nm=pred.ic50_nm,
                binding_percentile=pred.binding_percentile or 0.0,
                binding_strength=pred.binding_strength,
                binding_score=pred.binding_score,
                evidence_score=evidence_score,
                composite_score=total,
            )
        )
    return sorted(scored, key=lambda item: item.composite_score, reverse=True)
