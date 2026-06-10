from __future__ import annotations

import json
import platform
from pathlib import Path

import typer

from griffin import __version__
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
    checks = {
        "griffin_version": __version__,
        "python": platform.python_version(),
        "mock_mode": settings.mock_mode,
        "cache_dir": str(settings.cache_dir),
        "ncbi_email_configured": bool(settings.ncbi_email),
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
    top_n_evidence: int = typer.Option(20, "--top-n-evidence"),
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
            top_n_evidence=top_n_evidence,
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
