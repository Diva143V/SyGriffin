from __future__ import annotations

from griffin.core.hashing import stable_hash
from griffin.core.models import PubMedRecord


class PubMedClient:
    def __init__(self, email: str | None = None, api_key: str | None = None, mock: bool = True):
        self.email = email
        self.api_key = api_key
        self.mock = mock

    def search(self, query: str, max_results: int = 5) -> list[PubMedRecord]:
        if max_results <= 0:
            return []
        if not self.mock:
            return []
        mock_id = f"mock_pubmed_{int(stable_hash(query)[:8], 16) % 999 + 1:03d}"
        return [
            PubMedRecord(
                pmid=None,
                title=None,
                year=None,
                journal=None,
                evidence_level=self._level_for_query(query),
                url=None,
                query=query,
                source="mock",
                is_mock=True,
                mock_id=mock_id,
            )
        ]

    def _level_for_query(self, query: str) -> str:
        lowered = query.lower()
        if "neoantigen" in lowered:
            return "mutation_cancer_evidence"
        if "vaccine" in lowered:
            return "gene_pathway_evidence"
        return "weak_or_no_evidence"
