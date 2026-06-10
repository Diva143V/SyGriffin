from __future__ import annotations

from griffin.adapters.llm.base import EvidenceSummarizer
from griffin.core.models import EvidenceRecord


class NoLLMSummarizer(EvidenceSummarizer):
    name = "none"

    def available(self) -> bool:
        return True

    def summarize(self, evidence: list[EvidenceRecord]) -> str:
        if not evidence:
            return "LLM summarization: disabled. No evidence records were retrieved."
        return "LLM summarization: disabled. Evidence summaries use deterministic templates."
