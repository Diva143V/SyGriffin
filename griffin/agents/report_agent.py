from __future__ import annotations

from pathlib import Path

from griffin.reports.markdown_report import generate_markdown_report


class ReportAgent:
    def write(self, run_dir: Path, generate_pdf: bool = False) -> Path:
        return generate_markdown_report(run_dir, generate_pdf=generate_pdf)
