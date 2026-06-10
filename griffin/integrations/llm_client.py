from __future__ import annotations


class LLMClient:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def summarize(self, text: str) -> str:
        return text
