from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import typer

from griffin import __version__
from griffin.adapters.llm.ollama import OllamaSummarizer
from griffin.adapters.mhc.mhcflurry import MHCflurryPredictor
from griffin.bio.hla import validate_hla_alleles
from griffin.bio.vcf_parser import parse_vcf
from griffin.config.settings import ensure_project, load_settings, write_default_config
from griffin.core.exceptions import GriffinError
from griffin.core.models import RunConfig
from griffin.pipeline.runner import PipelineRunner
from griffin.reports.markdown_report import regenerate_report

app = typer.Typer(help="Griffin CLI research pipeline for neoantigen discovery.")


def _handle_error(exc: Exception) -> None:
    if isinstance(exc, GriffinError):
        raise typer.BadParameter(str(exc)) from exc
    raise exc


@app.command()
def init(
    project_dir: Path = typer.Option(Path("."), "--project-dir", help="Project root."),
) -> None:
    """Create Griffin project folders and default config."""
    ensure_project(project_dir)
    write_default_config(project_dir / ".griffin" / "config.yaml")
    typer.echo(f"Initialized Griffin project at {project_dir.resolve()}")


@app.command()
def doctor() -> None:
    """Check local environment."""
    settings = load_settings()
    ollama = OllamaSummarizer(settings.ollama_model, settings.ollama_base_url)
    ollama_diagnostic = ollama.probe()
    mhcflurry = MHCflurryPredictor()
    mhcflurry_available = mhcflurry.available()
    mhcflurry_downloads_available = mhcflurry.downloads_available()
    scientific_python_warning = None
    if sys.version_info >= (3, 13):
        scientific_python_warning = (
            "Python 3.11 is recommended for scientific dependencies such as MHCflurry. "
            "Current Python can still run Griffin demo/mock mode."
        )
    checks = {
        "griffin_version": __version__,
        "python": platform.python_version(),
        "scientific_python_recommended": "3.11",
        "scientific_python_warning": scientific_python_warning,
        "mock_mode_default": False,
        "mhcflurry_available": mhcflurry_available,
        "mhcflurry_version": mhcflurry.version() if mhcflurry_available else None,
        "mhcflurry_downloads_available": mhcflurry_downloads_available,
        "scientific_mhc_ready": mhcflurry_available and mhcflurry_downloads_available,
        "cache_dir": str(settings.cache_dir),
        "ncbi_email_configured": bool(settings.ncbi_email),
        "ollama_reachable": ollama_diagnostic["reachable"],
        "ollama_base_url": ollama_diagnostic["base_url"],
        "available_ollama_models": ollama_diagnostic["models"],
        "default_ollama_model": settings.ollama_model,
        "write_permissions": Path(".").resolve().exists(),
    }
    typer.echo(json.dumps(checks, indent=2, sort_keys=True))


@app.command("validate-input")
def validate_input(
    vcf: Path = typer.Option(..., "--vcf", exists=True, readable=True),
    hla: list[str] = typer.Option(..., "--hla", help="HLA allele, repeatable."),
    cancer_type: str = typer.Option(..., "--cancer-type"),
) -> None:
    """Validate VCF, HLA alleles, and cancer type metadata."""
    try:
        variants = parse_vcf(vcf)
        validate_hla_alleles(hla)
        if not cancer_type.strip():
            raise GriffinError("Cancer type is required.")
    except Exception as exc:
        _handle_error(exc)
    typer.echo(f"Input valid: {len(variants)} variants, {len(hla)} HLA alleles, {cancer_type}")


@app.command()
def run(
    vcf: Path = typer.Option(..., "--vcf", exists=True, readable=True),
    hla: list[str] = typer.Option(..., "--hla", help="HLA allele, repeatable."),
    cancer_type: str = typer.Option(..., "--cancer-type"),
    sample_id: str = typer.Option(..., "--sample-id"),
    out: Path = typer.Option(..., "--out"),
    genome_assembly: str = typer.Option("GRCh38", "--genome-assembly"),
    top_n_evidence: int = typer.Option(20, "--top-n-evidence"),
    mock: bool = typer.Option(False, "--mock", help="Use deterministic mock scientific adapters."),
    use_llm: bool = typer.Option(False, "--use-llm", help="Enable optional LLM summarization."),
    llm_provider: str = typer.Option("none", "--llm-provider"),
    ollama_model: str = typer.Option("phi3", "--ollama-model"),
    pdf: bool = typer.Option(False, "--pdf", help="Generate optional PDF report."),
) -> None:
    """Run the full Griffin pipeline."""
    try:
        config = RunConfig(
            sample_id=sample_id,
            vcf_path=vcf,
            hla_alleles=hla,
            cancer_type=cancer_type,
            output_dir=out,
            genome_assembly=genome_assembly,
            top_n_evidence=top_n_evidence,
            mock_mode=mock,
            use_llm=use_llm,
            llm_provider=llm_provider,
            ollama_model=ollama_model,
            generate_pdf=pdf,
        )
        result = PipelineRunner(config).run()
    except Exception as exc:
        _handle_error(exc)
    typer.echo(f"Run complete: {result.output_dir}")


@app.command()
def resume(run_dir: Path = typer.Option(..., "--run-dir", exists=True, file_okay=False)) -> None:
    """Resume a previous Griffin run from its resolved config."""
    try:
        result = PipelineRunner.from_run_dir(run_dir).run(resume=True)
    except Exception as exc:
        _handle_error(exc)
    typer.echo(f"Resume complete: {result.output_dir}")


@app.command()
def report(
    run_dir: Path = typer.Option(..., "--run-dir", exists=True, file_okay=False),
    pdf: bool = typer.Option(False, "--pdf"),
) -> None:
    """Regenerate report from existing artifacts."""
    try:
        path = regenerate_report(run_dir, generate_pdf=pdf)
    except Exception as exc:
        _handle_error(exc)
    typer.echo(f"Report written: {path}")


@app.command("version")
def version_command() -> None:
    """Print Griffin and runtime versions."""
    typer.echo(
        json.dumps(
            {
                "griffin": __version__,
                "python": platform.python_version(),
                "platform": platform.platform(),
            },
            indent=2,
        )
    )
