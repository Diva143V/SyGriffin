from __future__ import annotations

from pathlib import Path

import pytest
import requests

from griffin.core.exceptions import GriffinError
from griffin.core.models import VariantRecord
from griffin.integrations.vep_client import VEPClient


class FakeResponse:
    def __init__(self, payload, status_code: int = 200, text: str = ""):
        self.payload = payload
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.text = text

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _variant() -> VariantRecord:
    return VariantRecord(
        variant_id="chr7:140453136:A:T",
        chrom="7",
        pos=140453136,
        ref="A",
        alt="T",
    )


def _vep_payload():
    return [
        {
            "input": "7 140453136 chr7:140453136:A:T A T . . .",
            "most_severe_consequence": "missense_variant",
            "transcript_consequences": [
                {
                    "gene_symbol": "BRAF",
                    "gene_id": "ENSG00000157764",
                    "transcript_id": "ENST_FALLBACK",
                    "protein_id": "ENSP_FALLBACK",
                    "biotype": "protein_coding",
                    "consequence_terms": ["missense_variant"],
                    "impact": "MODERATE",
                    "protein_start": 600,
                    "amino_acids": "V/E",
                },
                {
                    "gene_symbol": "BRAF",
                    "gene_id": "ENSG00000157764",
                    "transcript_id": "ENST_CANONICAL",
                    "protein_id": "ENSP_CANONICAL",
                    "biotype": "protein_coding",
                    "canonical": 1,
                    "consequence_terms": ["missense_variant"],
                    "impact": "MODERATE",
                    "protein_start": 600,
                    "amino_acids": "V/E",
                    "hgvsc": "ENST_CANONICAL:c.1799T>A",
                    "hgvsp": "ENSP_CANONICAL:p.Val600Glu",
                },
                {
                    "gene_symbol": "BRAF",
                    "gene_id": "ENSG00000157764",
                    "transcript_id": "ENST_MANE",
                    "protein_id": "ENSP_MANE",
                    "biotype": "protein_coding",
                    "canonical": 1,
                    "mane_select": "NM_004333.6",
                    "consequence_terms": ["missense_variant"],
                    "impact": "HIGH",
                    "protein_start": 600,
                    "amino_acids": "V/E",
                    "codons": "gTg/gAg",
                    "hgvsc": "ENST_MANE:c.1799T>A",
                    "hgvsp": "ENSP_MANE:p.Val600Glu",
                },
            ],
        }
    ]


def test_real_vep_annotation_selects_mane_and_records_provenance(tmp_path: Path):
    session = FakeSession([FakeResponse(_vep_payload())])
    client = VEPClient(
        mock=False,
        cache_dir=tmp_path / "cache",
        raw_artifact_dir=tmp_path / "artifacts",
        session=session,
    )

    annotation = client.annotate_variants([_variant()])[0]

    assert annotation.annotation_source == "ensembl_vep_rest"
    assert annotation.assembly == "GRCh38"
    assert annotation.gene == "BRAF"
    assert annotation.gene_id == "ENSG00000157764"
    assert annotation.transcript == "ENST_MANE"
    assert annotation.protein_id == "ENSP_MANE"
    assert annotation.coding_dna_change == "ENST_MANE:c.1799T>A"
    assert annotation.protein_change == "p.Val600Glu"
    assert annotation.amino_acid_position == 600
    assert annotation.reference_amino_acid == "V"
    assert annotation.alternate_amino_acid == "E"
    assert annotation.canonical_transcript is True
    assert annotation.mane_transcript is True
    assert annotation.transcript_selection_reason == "mane_select"
    assert len(annotation.considered_transcripts) == 3
    assert annotation.raw_response_artifact is not None
    assert Path(annotation.raw_response_artifact).exists()
    assert session.calls[0]["params"]["mane"] == 1
    assert session.calls[0]["json"]["variants"] == ["7 140453136 chr7:140453136:A:T A T . . ."]


def test_real_vep_annotation_uses_cache_without_network(tmp_path: Path):
    first_session = FakeSession([FakeResponse(_vep_payload())])
    first_client = VEPClient(
        mock=False,
        cache_dir=tmp_path / "cache",
        raw_artifact_dir=tmp_path / "artifacts",
        session=first_session,
    )
    first_client.annotate_variants([_variant()])

    second_session = FakeSession([])
    second_client = VEPClient(
        mock=False,
        cache_dir=tmp_path / "cache",
        raw_artifact_dir=tmp_path / "artifacts",
        session=second_session,
    )
    annotation = second_client.annotate_variants([_variant()])[0]

    assert annotation.transcript == "ENST_MANE"
    assert second_session.calls == []


def test_real_vep_annotation_fails_on_empty_transcripts(tmp_path: Path):
    session = FakeSession([FakeResponse([{"input": "bad", "transcript_consequences": []}])])
    client = VEPClient(mock=False, cache_dir=tmp_path / "cache", session=session)

    with pytest.raises(GriffinError, match="no transcript consequences"):
        client.annotate_variants([_variant()])


def test_real_vep_annotation_fails_on_timeout(tmp_path: Path):
    session = FakeSession([requests.Timeout("slow")])
    client = VEPClient(mock=False, cache_dir=tmp_path / "cache", session=session, attempts=1)

    with pytest.raises(GriffinError, match="timed out"):
        client.annotate_variants([_variant()])


def test_vep_client_rejects_unsupported_assembly():
    with pytest.raises(GriffinError, match="Unsupported genome assembly"):
        VEPClient(mock=False, genome_assembly="T2T-CHM13")
