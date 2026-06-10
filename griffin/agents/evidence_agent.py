from __future__ import annotations

from griffin.bio.scoring import evidence_level_score
from griffin.core.models import EvidenceRecord, PeptideCandidate
from griffin.integrations.clinicaltrials_client import ClinicalTrialsClient
from griffin.integrations.pubmed_client import PubMedClient


class EvidenceAgent:
    def __init__(self, pubmed: PubMedClient, trials: ClinicalTrialsClient):
        self.pubmed = pubmed
        self.trials = trials

    def gather(
        self, candidates: list[PeptideCandidate], cancer_type: str, top_n: int
    ) -> list[EvidenceRecord]:
        records: list[EvidenceRecord] = []
        for candidate in candidates[:top_n]:
            mutation = candidate.protein_change or ""
            queries = [
                f"{candidate.gene} {mutation} {cancer_type} neoantigen".strip(),
                f"{candidate.gene} {cancer_type} vaccine",
                f"{candidate.gene} mutation T cell response",
                f"{candidate.gene} immunotherapy {cancer_type}",
            ]
            pubmed = []
            for query in queries[:2]:
                pubmed.extend(self.pubmed.search(query, max_results=1))
            trials = self.trials.search(
                cancer_type, [candidate.gene, "neoantigen", "personalized vaccine", "mRNA vaccine"]
            )
            level = pubmed[0].evidence_level if pubmed else "weak_or_no_evidence"
            records.append(
                EvidenceRecord(
                    candidate_id=candidate.candidate_id,
                    pubmed=pubmed,
                    clinical_trials=trials,
                    summary=(
                        f"Evidence for {candidate.gene} is computationally summarized for "
                        "research prioritization only."
                    ),
                    evidence_score=evidence_level_score(level),
                    evidence_level=level,
                    queries=queries,
                )
            )
        return records
