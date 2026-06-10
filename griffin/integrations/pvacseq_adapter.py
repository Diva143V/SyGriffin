from __future__ import annotations

from pathlib import Path

from griffin.core.models import PeptideCandidate


class PVACseqAdapter:
    def run(
        self,
        vcf_path: Path,
        hla_alleles: list[str],
        output_dir: Path,
    ) -> list[PeptideCandidate]:
        raise NotImplementedError("pVACseq integration is prepared for Phase 1.5.")
