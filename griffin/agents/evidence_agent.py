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
            for search_query in queries[:2]:
                pubmed.extend(self.pubmed.search(search_query, max_results=1))
            trials = self.trials.search(
                cancer_type, [candidate.gene, "neoantigen", "personalized vaccine", "mRNA vaccine"]
            )
            level = pubmed[0].evidence_level if pubmed else "weak_or_no_evidence"
            first_pubmed = pubmed[0] if pubmed else None
            primary_query: str | None = queries[0] if queries else None
            mock_records = bool(first_pubmed and first_pubmed.is_mock) or any(
                trial.is_mock for trial in trials
            )
            mock_id = None
            if first_pubmed and first_pubmed.is_mock:
                mock_id = first_pubmed.mock_id
            elif trials and trials[0].is_mock:
                mock_id = trials[0].mock_id
            records.append(
                EvidenceRecord(
                    candidate_id=candidate.candidate_id,
                    gene=candidate.gene,
                    mutation=candidate.mutation or candidate.protein_change,
                    query=primary_query,
                    source=first_pubmed.source if first_pubmed else "PubMed",
                    pmid=first_pubmed.pmid if first_pubmed else None,
                    title=first_pubmed.title if first_pubmed else None,
                    year=first_pubmed.year if first_pubmed else None,
                    journal=first_pubmed.journal if first_pubmed else None,
                    url=first_pubmed.url if first_pubmed else None,
                    evidence_type=level,
                    is_mock=mock_records,
                    mock_id=mock_id,
                    pubmed=pubmed,
                    clinical_trials=trials,
                    summary=(
                        (
                            "Mock evidence records were generated for demo/testing only. No real "
                            "PubMed or ClinicalTrials.gov records were retrieved."
                        )
                        if mock_records
                        else (
                            f"Evidence for {candidate.gene} {candidate.mutation or ''} is "
                            "summarized for research prioritization only."
                        )
                        if pubmed or trials
                        else (
                            "No evidence records retrieved. Evidence score was computed as 0.0 "
                            "or unavailable."
                        )
                    ),
                    evidence_score=evidence_level_score(level),
                    evidence_level=level,
                    queries=queries,
                )
            )
        return records
