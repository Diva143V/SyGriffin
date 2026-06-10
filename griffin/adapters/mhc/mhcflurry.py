from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
from typing import Any

from griffin.adapters.mhc.base import MHCPredictor
from griffin.bio.scoring import binding_score_from_ic50, binding_strength
from griffin.core.models import MHCPrediction, PeptideCandidate


class MHCflurryPredictor(MHCPredictor):
    name = "mhcflurry"

    def available(self) -> bool:
        return importlib.util.find_spec("mhcflurry") is not None

    def version(self) -> str | None:
        try:
            return importlib.metadata.version("mhcflurry")
        except importlib.metadata.PackageNotFoundError:
            return None

    def predict(self, peptides: list[PeptideCandidate]) -> list[MHCPrediction]:
        mhcflurry = importlib.import_module("mhcflurry")
        predictor = mhcflurry.Class1AffinityPredictor.load()
        rows: list[MHCPrediction] = []
        version = self.version()
        for candidate in peptides:
            raw = predictor.predict(
                peptides=[candidate.peptide],
                alleles=[candidate.hla],
            )
            raw_record = self._first_record(raw)
            ic50 = float(raw_record.get("prediction", raw_record.get("ic50", 0.0)))
            percentile = raw_record.get("prediction_percentile")
            rows.append(
                MHCPrediction(
                    candidate_id=candidate.candidate_id,
                    hla=candidate.hla,
                    peptide=candidate.peptide,
                    ic50_nm=round(ic50, 2),
                    binding_percentile=float(percentile) if percentile is not None else None,
                    binding_strength=binding_strength(ic50),
                    binding_score=binding_score_from_ic50(ic50),
                    predictor=self.name,
                    predictor_name=self.name,
                    predictor_version=version,
                    raw_output=raw_record,
                    is_mock=False,
                    mock=False,
                )
            )
        return rows

    def _first_record(self, raw: Any) -> dict[str, Any]:
        if hasattr(raw, "to_dict"):
            records = raw.to_dict(orient="records")
            return dict(records[0]) if records else {}
        if isinstance(raw, list) and raw:
            return dict(raw[0])
        if isinstance(raw, dict):
            return dict(raw)
        return {}
