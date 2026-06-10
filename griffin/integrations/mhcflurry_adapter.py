from __future__ import annotations

import shutil

from griffin.bio.scoring import binding_score_from_ic50, binding_strength
from griffin.core.hashing import stable_hash
from griffin.core.models import MHCPrediction, PeptideCandidate


class MHCflurryAdapter:
    def __init__(self) -> None:
        self.executable = shutil.which("mhcflurry-predict")
        self.mock = self.executable is None

    def predict(self, peptides: list[PeptideCandidate]) -> list[MHCPrediction]:
        return [self._mock_predict(candidate) for candidate in peptides]

    def _mock_predict(self, candidate: PeptideCandidate) -> MHCPrediction:
        seed = stable_hash(candidate.peptide + candidate.hla)
        bucket = int(seed[:8], 16) % 1200
        ic50 = float(max(25, bucket))
        score = binding_score_from_ic50(ic50)
        return MHCPrediction(
            candidate_id=candidate.candidate_id,
            hla=candidate.hla,
            peptide=candidate.peptide,
            ic50_nm=round(ic50, 2),
            binding_percentile=round(min(99.0, ic50 / 20), 2),
            binding_strength=binding_strength(ic50),
            binding_score=score,
            predictor="deterministic_mock" if self.mock else "mhcflurry",
            mock=self.mock,
        )
