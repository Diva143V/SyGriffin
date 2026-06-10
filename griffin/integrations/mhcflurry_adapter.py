from __future__ import annotations

import shutil

from griffin.adapters.mhc.mock import DeterministicMockMHCPredictor
from griffin.core.models import MHCPrediction, PeptideCandidate


class MHCflurryAdapter:
    def __init__(self) -> None:
        self.executable = shutil.which("mhcflurry-predict")
        self.mock = self.executable is None
        self._mock_predictor = DeterministicMockMHCPredictor()

    def predict(self, peptides: list[PeptideCandidate]) -> list[MHCPrediction]:
        return self._mock_predictor.predict(peptides)

    def _mock_predict(self, candidate: PeptideCandidate) -> MHCPrediction:
        return self._mock_predictor._predict_one(candidate)
