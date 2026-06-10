from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class GriffinModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Path: str}


class RunConfig(GriffinModel):
    sample_id: str
    vcf_path: Path
    hla_alleles: list[str]
    cancer_type: str
    output_dir: Path
    top_n_evidence: int = 20
    peptide_lengths: list[int] = Field(default_factory=lambda: [9, 10, 11])
    use_llm: bool = False
    llm_provider: str = "none"
    ollama_model: str = "phi3"
    generate_pdf: bool = False
    mock_mode: bool = False


class SampleMetadata(GriffinModel):
    sample_id: str
    cancer_type: str
    hla_alleles: list[str]


class VariantRecord(GriffinModel):
    variant_id: str
    chrom: str
    pos: int
    ref: str
    alt: str
    qual: str | None = None
    filter: str | None = None
    info: dict[str, str] = Field(default_factory=dict)


class AnnotatedVariant(VariantRecord):
    gene: str = "UNKNOWN"
    transcript: str | None = None
    protein_change: str | None = None
    consequence: str = "unknown"
    impact: str = "MODIFIER"
    impact_score: float = 0.1


class PeptideCandidate(GriffinModel):
    candidate_id: str
    variant_id: str
    source_variant_id: str | None = None
    chromosome: str | None = None
    position: int | None = None
    ref: str | None = None
    alt: str | None = None
    gene: str
    transcript: str | None = None
    mutation: str | None = None
    protein_change: str | None = None
    hla: str
    peptide: str
    peptide_length: int
    mutation_position_in_peptide: int | None = None
    presentation_score: float
    mutation_impact_score: float


class MHCPrediction(GriffinModel):
    candidate_id: str
    hla: str
    peptide: str
    ic50_nm: float
    binding_percentile: float | None = None
    binding_strength: str
    binding_score: float
    predictor: str | None = None
    predictor_name: str
    predictor_version: str | None = None
    raw_output: dict[str, Any] = Field(default_factory=dict)
    is_mock: bool = False
    mock: bool = False


class PubMedRecord(GriffinModel):
    pmid: str | None
    title: str | None
    year: int | None = None
    journal: str | None = None
    evidence_level: str
    url: str
    query: str | None = None
    source: str = "PubMed"
    is_mock: bool = False


class ClinicalTrialRecord(GriffinModel):
    nct_id: str
    title: str
    status: str | None = None
    phase: str | None = None
    url: str
    query: str | None = None


class EvidenceRecord(GriffinModel):
    candidate_id: str
    gene: str | None = None
    mutation: str | None = None
    query: str | None = None
    source: str = "PubMed"
    pmid: str | None = None
    title: str | None = None
    year: int | None = None
    journal: str | None = None
    url: str | None = None
    evidence_type: str = "mutation_cancer_evidence"
    is_mock: bool = False
    pubmed: list[PubMedRecord] = Field(default_factory=list)
    clinical_trials: list[ClinicalTrialRecord] = Field(default_factory=list)
    summary: str
    evidence_score: float
    evidence_level: str
    queries: list[str] = Field(default_factory=list)


class ScoredCandidate(PeptideCandidate):
    ic50_nm: float
    binding_percentile: float
    binding_strength: str
    binding_score: float
    evidence_score: float = 0.0
    composite_score: float
    confidence_label: str = "insufficient_evidence"
    rationale: str = ""


class FinalCandidate(ScoredCandidate):
    rank: int
    limitations: list[str] = Field(default_factory=list)


class ReportSection(GriffinModel):
    title: str
    body: str


class RunManifest(GriffinModel):
    sample_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str = "running"
    mock_mode: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)
    input_hashes: dict[str, str] = Field(default_factory=dict)
    tool_versions: dict[str, str] = Field(default_factory=dict)
    api_queries: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checkpoints: list[str] = Field(default_factory=list)


def model_to_dict(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(mode="json")  # type: ignore[attr-defined]
    return _json_ready(model.dict())


def model_copy(model: BaseModel, update: dict[str, Any]) -> BaseModel:
    if hasattr(model, "model_copy"):
        return model.model_copy(update=update)  # type: ignore[attr-defined]
    return model.copy(update=update)


def _json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value
