from __future__ import annotations

import sys
import types

import griffin.adapters.mhc.mhcflurry as mhcflurry_module
from griffin.adapters.mhc.mhcflurry import MHCflurryPredictor
from griffin.core.models import PeptideCandidate


def test_mhcflurry_predictor_uses_real_prediction_dataframe(monkeypatch):
    class FakeFrame:
        def to_dict(self, orient):
            assert orient == "records"
            return [
                {
                    "peptide": "SLYNTVATL",
                    "allele": "HLA-A*02:01",
                    "prediction": 35.3536,
                    "prediction_percentile": 0.2427,
                }
            ]

    class FakeLoadedPredictor:
        def predict_to_dataframe(self, peptides, alleles):
            assert peptides == ["SLYNTVATL"]
            assert alleles == ["HLA-A*02:01"]
            return FakeFrame()

    class FakeClass1AffinityPredictor:
        @staticmethod
        def load():
            return FakeLoadedPredictor()

    fake_mhcflurry = types.ModuleType("mhcflurry")
    fake_mhcflurry.Class1AffinityPredictor = FakeClass1AffinityPredictor
    monkeypatch.setitem(sys.modules, "mhcflurry", fake_mhcflurry)
    monkeypatch.setattr(
        mhcflurry_module.importlib.metadata,
        "version",
        lambda package: "9.9.9" if package == "mhcflurry" else None,
    )

    prediction = MHCflurryPredictor().predict(
        [
            PeptideCandidate(
                candidate_id="cand_test",
                variant_id="variant_test",
                gene="BRAF",
                hla="HLA-A*02:01",
                peptide="SLYNTVATL",
                peptide_length=9,
                presentation_score=0.0,
                mutation_impact_score=0.0,
            )
        ]
    )[0]

    assert prediction.ic50_nm == 35.35
    assert prediction.binding_percentile == 0.2427
    assert prediction.binding_score == 1.0
    assert prediction.predictor_name == "mhcflurry"
    assert prediction.predictor_version == "9.9.9"
    assert prediction.raw_output["prediction"] == 35.3536
    assert prediction.is_mock is False
