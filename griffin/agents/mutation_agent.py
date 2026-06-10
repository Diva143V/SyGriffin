from __future__ import annotations

from pathlib import Path

from griffin.bio.vcf_parser import parse_vcf
from griffin.core.models import AnnotatedVariant
from griffin.integrations.vep_client import VEPClient


class MutationAgent:
    def __init__(self, vep_client: VEPClient):
        self.vep_client = vep_client

    def run(self, vcf_path: Path) -> list[AnnotatedVariant]:
        return self.vep_client.annotate_variants(parse_vcf(vcf_path))
