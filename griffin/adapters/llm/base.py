from __future__ import annotations

from griffin.core.models import EvidenceRecord


class EvidenceSummarizer:
    name: str = "base"

    def available(self) -> bool:
        raise NotImplementedError

    def summarize(self, evidence: list[EvidenceRecord]) -> str:
        raise NotImplementedError
