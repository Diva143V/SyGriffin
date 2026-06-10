from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from griffin.reports.pdf_report import write_pdf

DISCLAIMER = (
    "Research Use Only: Griffin is a computational research acceleration tool. It does not "
    "provide clinical diagnosis, treatment recommendations, or medical advice. All candidates "
    "require independent wet-lab validation and expert review."
)


def generate_markdown_report(run_dir: Path, generate_pdf: bool = False) -> Path:
    outputs_dir = run_dir / "outputs"
    artifacts_dir = run_dir / "artifacts"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "run_manifest.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    )
    candidates = json.loads((artifacts_dir / "final_candidates.json").read_text(encoding="utf-8"))
    evidence = json.loads((artifacts_dir / "evidence.json").read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.md.j2")
    content = template.render(
        disclaimer=DISCLAIMER,
        manifest=manifest,
        candidates=candidates,
        evidence=evidence,
        warnings=manifest.get("warnings", []),
        label_display={
            "high_computational_priority": "High computational priority for research follow-up",
            "moderate_computational_priority": "Moderate computational priority for research follow-up",
            "low_computational_priority": "Low computational priority for research follow-up",
            "insufficient_evidence": "Insufficient evidence for computational prioritization",
        },
    )
    report_path = outputs_dir / "report.md"
    report_path.write_text(content, encoding="utf-8")
    if generate_pdf:
        write_pdf(outputs_dir / "report.pdf", content)
    return report_path


def regenerate_report(run_dir: Path, generate_pdf: bool = False) -> Path:
    return generate_markdown_report(run_dir, generate_pdf=generate_pdf)
