from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
from typing import Any

from griffin.adapters.mhc.base import MHCPredictor
from griffin.bio.scoring import binding_score_from_ic50, binding_strength
from griffin.core.exceptions import GriffinError
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

    def downloads_available(self) -> bool:
        if not self.available():
            return False
        try:
            mhcflurry = importlib.import_module("mhcflurry")
            mhcflurry.Class1AffinityPredictor.load()
        except Exception:
            return False
        return True

    def predict(self, peptides: list[PeptideCandidate]) -> list[MHCPrediction]:
        mhcflurry = importlib.import_module("mhcflurry")
        predictor = mhcflurry.Class1AffinityPredictor.load()
        rows: list[MHCPrediction] = []
        version = self.version()
        for candidate in peptides:
            raw = self._predict_one_raw(predictor, candidate)
            raw_record = self._first_record(raw)
            ic50_value = raw_record.get("prediction", raw_record.get("ic50"))
            if ic50_value is None:
                raise GriffinError(
                    "MHCflurry returned no prediction value. No synthetic IC50 was generated."
                )
            ic50 = float(ic50_value)
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

    def _predict_one_raw(self, predictor: Any, candidate: PeptideCandidate) -> Any:
        if hasattr(predictor, "predict_to_dataframe"):
            return predictor.predict_to_dataframe(
                peptides=[candidate.peptide],
                alleles=[candidate.hla],
            )
        return predictor.predict(
            peptides=[candidate.peptide],
            alleles=[candidate.hla],
        )

    def _first_record(self, raw: Any) -> dict[str, Any]:
        if hasattr(raw, "to_dict"):
            records = raw.to_dict(orient="records")
            return self._json_ready_record(dict(records[0])) if records else {}
        if isinstance(raw, list) and raw:
            return self._json_ready_record(dict(raw[0]))
        if isinstance(raw, dict):
            return self._json_ready_record(dict(raw))
        if hasattr(raw, "tolist"):
            values = raw.tolist()
            if isinstance(values, list) and values:
                return {"prediction": self._json_ready_value(values[0])}
            return {}
        return {}

    def _json_ready_record(self, record: dict[str, Any]) -> dict[str, Any]:
        return {key: self._json_ready_value(value) for key, value in record.items()}

    def _json_ready_value(self, value: Any) -> Any:
        if hasattr(value, "item"):
            return value.item()
        return value
