from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from griffin.adapters.llm.none import NoLLMSummarizer
from griffin.adapters.llm.ollama import OllamaSummarizer
from griffin.adapters.mhc.base import mhc_unavailable_message
from griffin.adapters.mhc.mhcflurry import MHCflurryPredictor
from griffin.adapters.mhc.mock import DeterministicMockMHCPredictor
from griffin.agents.evidence_agent import EvidenceAgent
from griffin.agents.mutation_agent import MutationAgent
from griffin.agents.neoantigen_agent import NeoantigenAgent
from griffin.agents.report_agent import ReportAgent
from griffin.agents.research_lead import ResearchLeadAgent
from griffin.bio.hla import validate_hla_alleles
from griffin.bio.scoring import score_candidates
from griffin.bio.vcf_parser import parse_vcf
from griffin.config.settings import load_settings
from griffin.core.checkpoints import CheckpointStore
from griffin.core.exceptions import GriffinError
from griffin.core.hashing import sha256_file
from griffin.core.logging import configure_logging
from griffin.core.manifest import create_manifest, load_manifest, write_manifest
from griffin.core.models import PeptideCandidate, RunConfig, model_to_dict
from griffin.integrations.clinicaltrials_client import ClinicalTrialsClient
from griffin.integrations.pubmed_client import PubMedClient
from griffin.integrations.vep_client import VEPClient
from griffin.pipeline.context import PipelineContext


class PipelineRunner:
    def __init__(self, config: RunConfig):
        self.config = config

    @classmethod
    def from_run_dir(cls, run_dir: Path) -> PipelineRunner:
        config_path = run_dir / "config.resolved.yaml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return cls(RunConfig(**data))

    def run(self, resume: bool = False) -> PipelineContext:
        settings = load_settings(cli_overrides={"mock_mode": self.config.mock_mode})
        input_hash = sha256_file(self.config.vcf_path)
        manifest_path = self.config.output_dir / "run_manifest.json"
        if resume and manifest_path.exists():
            manifest = load_manifest(manifest_path)
        else:
            manifest = create_manifest(self.config, input_hash)
        ctx = PipelineContext(self.config, manifest)
        ctx.ensure_dirs()
        configure_logging(ctx.logs_dir, settings.log_level)
        checkpoints = CheckpointStore(ctx.checkpoints_dir)
        predictor = self._select_mhc_predictor()
        predictor_version = self._predictor_version(predictor)
        ctx.manifest.parameters["mock_mode"] = self.config.mock_mode
        ctx.manifest.parameters["genome_assembly"] = self.config.genome_assembly
        ctx.manifest.tool_versions["mhc_predictor"] = predictor.name
        if predictor_version:
            ctx.manifest.tool_versions["mhc_predictor_version"] = predictor_version
        ctx.manifest.scientific_provenance = self._scientific_provenance(
            predictor.name,
            predictor_version,
        )
        if self.config.mock_mode:
            self._warn(
                ctx,
                "Mock mode is enabled. Deterministic mock predictions and mock evidence are "
                "for demo/testing only.",
            )

        self._stage(checkpoints, "01_input_validation", lambda: self._validate_inputs())
        self._prepare_inputs(ctx, input_hash)
        raw_variants = self._stage(
            checkpoints,
            "02_vcf_parsing",
            lambda: self._write_json(
                ctx.artifact("variants.raw.json"),
                parse_vcf(self.config.vcf_path),
            ),
        )
        annotated = self._stage(
            checkpoints,
            "03_variant_annotation",
            lambda: self._write_json(
                ctx.artifact("variants.annotated.json"),
                MutationAgent(
                    VEPClient(
                        mock=settings.mock_mode,
                        genome_assembly=self.config.genome_assembly,
                        cache_dir=settings.cache_dir / "vep",
                        raw_artifact_dir=ctx.artifacts_dir,
                    )
                ).vep_client.annotate_variants(raw_variants),
            ),
        )
        self._stage(checkpoints, "04_mutation_scoring", lambda: annotated)
        neo_agent = NeoantigenAgent()
        peptides = self._stage(
            checkpoints,
            "05_peptide_generation",
            lambda: self._write_json(
                ctx.artifact("peptides.generated.json"),
                neo_agent.generate(
                    annotated,
                    self.config.hla_alleles,
                    self.config.peptide_lengths,
                    mock_mode=settings.mock_mode,
                ),
            ),
        )
        predictions = self._stage(
            checkpoints,
            "06_mhc_prediction",
            lambda: self._write_json(
                ctx.artifact("mhc_predictions.json"),
                predictor.predict(peptides),
            ),
        )
        filtered = self._stage(
            checkpoints,
            "07_candidate_filtering",
            lambda: [
                peptide
                for peptide in peptides
                if (
                    next(
                        pred for pred in predictions if pred.candidate_id == peptide.candidate_id
                    ).binding_score
                    >= 0.10
                )
            ],
        )
        evidence_agent = EvidenceAgent(
            PubMedClient(settings.ncbi_email, settings.ncbi_api_key, mock=settings.mock_mode),
            ClinicalTrialsClient(mock=settings.mock_mode),
        )
        if not settings.mock_mode and not settings.ncbi_email:
            self._warn(ctx, "NCBI_EMAIL is not configured. PubMed E-utilities were not queried.")
        evidence = self._stage(
            checkpoints,
            "08_evidence_search",
            lambda: self._write_json(
                ctx.artifact("evidence.json"),
                (
                    evidence_agent.gather(
                        filtered,
                        self.config.cancer_type,
                        self.config.top_n_evidence,
                    )
                    if settings.mock_mode
                    else []
                ),
            ),
        )
        if not evidence:
            self._warn(
                ctx,
                "No evidence records retrieved. Evidence score was computed as 0.0 or unavailable.",
            )
        filtered = self._apply_candidate_provenance(
            filtered,
            predictor.name,
            predictor_version,
            "mock" if settings.mock_mode else "pubmed_ncbi_eutilities",
        )
        ctx.manifest.api_queries = [
            {"candidate_id": record.candidate_id, "queries": record.queries} for record in evidence
        ]
        llm_summary = self._summarize_evidence(evidence)
        ctx.manifest.parameters["llm_summary"] = llm_summary
        scored = self._stage(
            checkpoints,
            "09_composite_scoring",
            lambda: self._write_json(
                ctx.artifact("candidates.scored.json"),
                score_candidates(filtered, predictions, evidence),
            ),
        )
        final = self._stage(
            checkpoints,
            "10_research_lead_review",
            lambda: self._write_json(
                ctx.artifact("final_candidates.json"), ResearchLeadAgent().review(scored)
            ),
        )
        self._stage(checkpoints, "11_exports", lambda: self._write_outputs(ctx, final, evidence))
        ctx.manifest.checkpoints = checkpoints.completed()
        write_manifest(ctx.output_dir / "run_manifest.json", ctx.manifest)
        write_manifest(ctx.output_dir / "manifest.json", ctx.manifest)
        self._stage(
            checkpoints,
            "12_markdown_report",
            lambda: ReportAgent().write(ctx.output_dir, False),
        )
        if self.config.generate_pdf:
            self._stage(
                checkpoints,
                "13_pdf_report",
                lambda: ReportAgent().write(ctx.output_dir, True),
            )
        else:
            checkpoints.mark_done("13_pdf_report")
        ctx.manifest.completed_at = datetime.now(timezone.utc)
        ctx.manifest.status = "completed"
        ctx.manifest.checkpoints = checkpoints.completed()
        write_manifest(ctx.output_dir / "run_manifest.json", ctx.manifest)
        write_manifest(ctx.output_dir / "manifest.json", ctx.manifest)
        checkpoints.mark_done("14_manifest_finalization")
        report_path = ReportAgent().write(ctx.output_dir, self.config.generate_pdf)
        shutil.copyfile(report_path, ctx.output_dir / "report.md")
        return ctx

    def _select_mhc_predictor(self):
        if self.config.mock_mode:
            return DeterministicMockMHCPredictor()
        predictor = MHCflurryPredictor()
        if predictor.available():
            return predictor
        raise GriffinError(mhc_unavailable_message())

    def _predictor_version(self, predictor: Any) -> str | None:
        version = getattr(predictor, "version", None)
        if callable(version):
            result = version()
            return str(result) if result else None
        return None

    def _scientific_provenance(
        self, predictor_name: str, predictor_version: str | None
    ) -> dict[str, Any]:
        mock_mode = self.config.mock_mode
        llm_provider = self.config.llm_provider if self.config.use_llm else "none"
        return {
            "mock_mode": mock_mode,
            "genome_assembly": self.config.genome_assembly,
            "mhc_predictor": predictor_name,
            "mhc_predictor_version": predictor_version,
            "variant_annotator": "mock" if mock_mode else "ensembl_vep_rest",
            "sequence_context_source": "mock" if mock_mode else "ensembl_or_uniprot",
            "evidence_source": "mock" if mock_mode else "pubmed_ncbi_eutilities",
            "trial_source": "mock" if mock_mode else "clinicaltrials_gov",
            "llm_provider": llm_provider,
            "llm_model": self.config.ollama_model if llm_provider == "ollama" else None,
            "llm_summary_source": self._llm_summary_source(mock_mode, llm_provider),
        }

    def _llm_summary_source(self, mock_mode: bool, llm_provider: str) -> str:
        if llm_provider == "none":
            return "deterministic_non_llm"
        if mock_mode:
            return "mock_evidence_only"
        return "retrieved_evidence_records"

    def _apply_candidate_provenance(
        self,
        candidates: list[PeptideCandidate],
        predictor_name: str,
        predictor_version: str | None,
        evidence_source: str,
    ) -> list[PeptideCandidate]:
        return [
            PeptideCandidate(
                **{
                    **model_to_dict(candidate),
                    "is_mock": self.config.mock_mode or candidate.is_mock,
                    "predictor_name": predictor_name,
                    "predictor_version": predictor_version,
                    "annotation_source": "mock" if self.config.mock_mode else "ensembl_vep_rest",
                    "sequence_context_source": "mock"
                    if self.config.mock_mode
                    else "ensembl_or_uniprot",
                    "evidence_source": evidence_source,
                }
            )
            for candidate in candidates
        ]

    def _summarize_evidence(self, evidence: Any) -> str:
        if not self.config.use_llm:
            return NoLLMSummarizer().summarize(evidence)
        if self.config.llm_provider != "ollama":
            raise GriffinError(
                "Unsupported LLM provider. Griffin currently supports --llm-provider ollama only."
            )
        settings = load_settings()
        return OllamaSummarizer(
            self.config.ollama_model,
            settings.ollama_base_url,
        ).summarize(evidence)

    def _warn(self, ctx: PipelineContext, warning: str) -> None:
        if warning not in ctx.manifest.warnings:
            ctx.manifest.warnings.append(warning)

    def _validate_inputs(self) -> bool:
        parse_vcf(self.config.vcf_path)
        validate_hla_alleles(self.config.hla_alleles)
        return True

    def _prepare_inputs(self, ctx: PipelineContext, input_hash: str) -> None:
        shutil.copyfile(self.config.vcf_path, ctx.inputs_dir / "input.vcf")
        (ctx.inputs_dir / "input.sha256").write_text(input_hash + "\n", encoding="utf-8")
        (ctx.output_dir / "config.resolved.yaml").write_text(
            yaml.safe_dump(model_to_dict(self.config), sort_keys=False), encoding="utf-8"
        )

    def _stage(self, checkpoints: CheckpointStore, name: str, fn: Any) -> Any:
        result = fn()
        checkpoints.mark_done(name)
        return result

    def _write_json(self, path: Path, records: Any) -> Any:
        serializable = (
            [model_to_dict(item) for item in records] if isinstance(records, list) else records
        )
        path.write_text(json.dumps(serializable, indent=2, sort_keys=True), encoding="utf-8")
        return records

    def _write_outputs(self, ctx: PipelineContext, final: Any, evidence: Any) -> bool:
        candidates_data = [model_to_dict(item) for item in final]
        evidence_data = [model_to_dict(item) for item in evidence]
        (ctx.outputs_dir / "candidates.json").write_text(
            json.dumps(candidates_data, indent=2, sort_keys=True), encoding="utf-8"
        )
        (ctx.outputs_dir / "evidence.json").write_text(
            json.dumps(evidence_data, indent=2, sort_keys=True), encoding="utf-8"
        )
        (ctx.output_dir / "candidates.json").write_text(
            json.dumps(candidates_data, indent=2, sort_keys=True), encoding="utf-8"
        )
        (ctx.output_dir / "evidence.json").write_text(
            json.dumps(evidence_data, indent=2, sort_keys=True), encoding="utf-8"
        )
        with (ctx.outputs_dir / "candidates.csv").open("w", encoding="utf-8", newline="") as handle:
            fieldnames = [
                "rank",
                "candidate_id",
                "source_variant_id",
                "chromosome",
                "position",
                "ref",
                "alt",
                "gene",
                "transcript",
                "mutation",
                "protein_change",
                "hla",
                "peptide",
                "peptide_length",
                "mutation_position_in_peptide",
                "ic50_nm",
                "binding_strength",
                "presentation_score",
                "mutation_impact_score",
                "evidence_score",
                "composite_score",
                "confidence_label",
            ]
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in candidates_data:
                writer.writerow({key: row.get(key) for key in fieldnames})
        shutil.copyfile(ctx.outputs_dir / "candidates.csv", ctx.output_dir / "candidates.csv")
        return True
