from pathlib import Path

from griffin.core.models import RunConfig
from griffin.pipeline.runner import PipelineRunner


def test_report_includes_disclaimer(fixture_dir: Path, tmp_path: Path):
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
    report = (run_dir / "outputs" / "report.md").read_text(encoding="utf-8")
    assert "Research Use Only" in report
    assert "## Scoring Formula" in report
    assert "Candidate ranking is based on computational prioritization signals" in report
    assert "Mock evidence ID:" in report
    assert "No real PubMed record was retrieved." in report
    assert "Mock trial ID:" in report
    assert "No real ClinicalTrials.gov record was retrieved." in report
