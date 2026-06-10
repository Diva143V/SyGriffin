from __future__ import annotations

from griffin.core.hashing import stable_hash
from griffin.core.models import ClinicalTrialRecord


class ClinicalTrialsClient:
    def __init__(self, mock: bool = True):
        self.mock = mock

    def search(self, condition: str, terms: list[str]) -> list[ClinicalTrialRecord]:
        if not self.mock:
            return []
        query = " ".join([condition, *terms])
        mock_id = f"mock_trial_{int(stable_hash(query)[:8], 16) % 999 + 1:03d}"
        return [
            ClinicalTrialRecord(
                nct_id=None,
                title=None,
                status=None,
                phase=None,
                url=None,
                query=query,
                source="mock",
                is_mock=True,
                mock_id=mock_id,
            )
        ]
