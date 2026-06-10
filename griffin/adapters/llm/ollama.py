from __future__ import annotations

import json
from typing import Any

import requests

from griffin.adapters.llm.base import EvidenceSummarizer
from griffin.core.exceptions import GriffinError
from griffin.core.models import EvidenceRecord, model_to_dict

OLLAMA_SYSTEM_PROMPT = """You are summarizing structured biomedical evidence records for research-use-only neoantigen prioritization.

Do not invent PMIDs, titles, years, trial IDs, genes, variants, or claims.
Only summarize the evidence records provided.
If evidence is weak or missing, say so clearly.
Do not provide diagnosis, treatment recommendation, medical advice, or clinical actionability.
Return concise research language."""


class OllamaSummarizer(EvidenceSummarizer):
    name = "ollama"

    def __init__(self, model: str = "phi3", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
        except requests.RequestException:
            return False
        return response.ok

    def models(self) -> list[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise GriffinError(
                "Ollama LLM unavailable. Griffin was run with --use-llm "
                "--llm-provider ollama, but http://localhost:11434 is not reachable. "
                "Start Ollama with `ollama serve` or rerun without --use-llm."
            ) from exc
        data = response.json()
        return [item.get("name", "") for item in data.get("models", [])]

    def ensure_available(self) -> None:
        names = self.models()
        if names and self.model not in names and f"{self.model}:latest" not in names:
            raise GriffinError(
                f"Ollama model '{self.model}' is not available locally. "
                f"Run `ollama pull {self.model}` or choose an installed model."
            )

    def summarize(self, evidence: list[EvidenceRecord]) -> str:
        self.ensure_available()
        payload = {
            "model": self.model,
            "stream": False,
            "prompt": (
                OLLAMA_SYSTEM_PROMPT
                + "\n\nEvidence records:\n"
                + json.dumps([self._safe_record(record) for record in evidence], indent=2)
            ),
        }
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=60)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise GriffinError(
                "Ollama LLM unavailable during summarization. No fake LLM output was generated."
            ) from exc
        data = response.json()
        return str(data.get("response", "")).strip()

    def _safe_record(self, record: EvidenceRecord) -> dict[str, Any]:
        data = model_to_dict(record)
        return {
            "candidate_id": data.get("candidate_id"),
            "gene": data.get("gene"),
            "mutation": data.get("mutation"),
            "source": data.get("source"),
            "pmid": data.get("pmid"),
            "title": data.get("title"),
            "year": data.get("year"),
            "journal": data.get("journal"),
            "url": data.get("url"),
            "evidence_type": data.get("evidence_type"),
            "is_mock": data.get("is_mock"),
            "summary": data.get("summary"),
        }
