from __future__ import annotations

from griffin.core.models import MHCPrediction, PeptideCandidate


def mhc_unavailable_message() -> str:
    return (
        "MHC predictor unavailable.\n\n"
        "Griffin is running in non-mock mode, but no real MHC prediction backend is available.\n\n"
        "Install/configure one of:\n"
        "- MHCflurry\n"
        "- NetMHCpan adapter\n"
        "- pVACseq adapter\n\n"
        "For demo/testing only, rerun with:\n"
        "  --mock"
    )


class MHCPredictor:
    name: str = "base"

    def available(self) -> bool:
        raise NotImplementedError

    def predict(self, peptides: list[PeptideCandidate]) -> list[MHCPrediction]:
        raise NotImplementedError
