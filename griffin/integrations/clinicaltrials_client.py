from __future__ import annotations

from griffin.core.models import ClinicalTrialRecord


class ClinicalTrialsClient:
    def __init__(self, mock: bool = True):
        self.mock = mock

    def search(self, condition: str, terms: list[str]) -> list[ClinicalTrialRecord]:
        query = " ".join([condition, *terms])
        return [
            ClinicalTrialRecord(
                nct_id="NCT00000000",
                title=f"Mock trial context for {query}",
                status="RECRUITING",
                phase="Phase 1",
                url="https://clinicaltrials.gov/",
                query=query,
            )
        ]
