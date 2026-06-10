import json
from pathlib import Path

from griffin.core.models import RunConfig
from griffin.pipeline.runner import PipelineRunner


def test_mock_run_outputs_evidence_and_traceability(fixture_dir: Path, tmp_path: Path):
    run_dir = tmp_path / "run"
    PipelineRunner(
        RunConfig(
            sample_id="demo",
            vcf_path=fixture_dir / "tiny.vcf",
            hla_alleles=["HLA-A*02:01"],
            cancer_type="melanoma",
            output_dir=run_dir,
            mock_mode=True,
        )
    ).run()

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    evidence = json.loads((run_dir / "evidence.json").read_text(encoding="utf-8"))
    candidates = json.loads((run_dir / "candidates.json").read_text(encoding="utf-8"))

    assert manifest["mock_mode"] is True
    assert manifest["scientific_provenance"]["mock_mode"] is True
    assert manifest["scientific_provenance"]["mhc_predictor"] == "deterministic_mock"
    assert manifest["scientific_provenance"]["variant_annotator"] == "mock"
    assert manifest["scientific_provenance"]["sequence_context_source"] == "mock"
    assert manifest["scientific_provenance"]["evidence_source"] == "mock"
    assert manifest["scientific_provenance"]["trial_source"] == "mock"
    for key in ["pmid", "title", "year", "source", "query", "url", "is_mock"]:
        assert key in evidence[0]
    assert evidence[0]["is_mock"] is True
    assert evidence[0]["mock_id"].startswith("mock_pubmed_")
    assert evidence[0]["pmid"] is None
    assert evidence[0]["url"] is None
    assert evidence[0]["pubmed"][0]["pmid"] is None
    assert evidence[0]["pubmed"][0]["url"] is None
    assert evidence[0]["pubmed"][0]["mock_id"].startswith("mock_pubmed_")
    assert evidence[0]["clinical_trials"][0]["nct_id"] is None
    assert evidence[0]["clinical_trials"][0]["url"] is None
    assert evidence[0]["clinical_trials"][0]["mock_id"].startswith("mock_trial_")
    for key in [
        "chromosome",
        "position",
        "ref",
        "alt",
        "peptide_length",
        "mutation_position_in_peptide",
        "is_mock",
        "predictor_name",
        "predictor_version",
        "annotation_source",
        "sequence_context_source",
        "evidence_source",
    ]:
        assert key in candidates[0]
    assert candidates[0]["is_mock"] is True
    assert candidates[0]["predictor_name"] == "deterministic_mock"
    assert candidates[0]["predictor_version"] == "0.1.0"
    assert candidates[0]["annotation_source"] == "mock"
    assert candidates[0]["sequence_context_source"] == "mock"
    assert candidates[0]["evidence_source"] == "mock"
