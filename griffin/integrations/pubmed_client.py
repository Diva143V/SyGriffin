from __future__ import annotations

from griffin.core.models import PubMedRecord


class PubMedClient:
    def __init__(self, email: str | None = None, api_key: str | None = None, mock: bool = True):
        self.email = email
        self.api_key = api_key
        self.mock = mock

    def search(self, query: str, max_results: int = 5) -> list[PubMedRecord]:
        if max_results <= 0:
            return []
        return [
            PubMedRecord(
                pmid=str(90000000 + abs(hash(query)) % 999999),
                title=f"Mock literature context for {query}",
                year=2024,
                journal="Griffin Mock Evidence",
                evidence_level=self._level_for_query(query),
                url="https://pubmed.ncbi.nlm.nih.gov/",
                query=query,
            )
        ]

    def _level_for_query(self, query: str) -> str:
        lowered = query.lower()
        if "neoantigen" in lowered:
            return "mutation_cancer_evidence"
        if "vaccine" in lowered:
            return "gene_pathway_evidence"
        return "weak_or_no_evidence"
