from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from griffin.core.exceptions import GriffinError
from griffin.core.hashing import stable_hash
from griffin.core.models import AnnotatedVariant, VariantRecord, model_to_dict

IMPACT_SCORES = {"HIGH": 0.91, "MODERATE": 0.62, "LOW": 0.25, "MODIFIER": 0.1}
ENSEMBL_REST_GRCH38 = "https://rest.ensembl.org"
ENSEMBL_REST_GRCH37 = "https://grch37.rest.ensembl.org"


class VEPClient:
    def __init__(
        self,
        mock: bool = True,
        genome_assembly: str = "GRCh38",
        cache_dir: Path | None = None,
        raw_artifact_dir: Path | None = None,
        timeout_seconds: float = 15.0,
        attempts: int = 3,
        base_url: str | None = None,
        session: Any | None = None,
    ):
        self.mock = mock
        self.genome_assembly = genome_assembly
        self.cache_dir = cache_dir
        self.raw_artifact_dir = raw_artifact_dir
        self.timeout_seconds = timeout_seconds
        self.attempts = attempts
        self.base_url = base_url or self._base_url_for_assembly(genome_assembly)
        self.session = session or requests.Session()

    def annotate_variants(self, variants: list[VariantRecord]) -> list[AnnotatedVariant]:
        if self.mock:
            return [self._mock_annotation(variant) for variant in variants]
        if not variants:
            return []
        self._validate_variants(variants)
        raw_records, raw_path, cache_key = self._fetch_or_load_raw(variants)
        return self._parse_response(variants, raw_records, raw_path, cache_key)

    def _fetch_or_load_raw(
        self, variants: list[VariantRecord]
    ) -> tuple[list[dict[str, Any]], Path | None, str]:
        payload = {"variants": [self._variant_to_vep_region(variant) for variant in variants]}
        params = self._request_params()
        cache_key = stable_hash(
            json.dumps(
                {
                    "assembly": self.genome_assembly,
                    "base_url": self.base_url,
                    "payload": payload,
                    "params": params,
                },
                sort_keys=True,
            )
        )
        cache_path = self._cache_path(cache_key)
        if cache_path and cache_path.exists():
            raw_records = json.loads(cache_path.read_text(encoding="utf-8"))
            artifact_path = self._write_raw_artifact(cache_key, raw_records)
            return self._ensure_record_list(raw_records), artifact_path or cache_path, cache_key

        raw_records = self._post_vep(payload, params)
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(raw_records, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        artifact_path = self._write_raw_artifact(cache_key, raw_records)
        return self._ensure_record_list(raw_records), artifact_path or cache_path, cache_key

    def _post_vep(self, payload: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/vep/homo_sapiens/region"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        last_error: Exception | None = None
        for attempt in range(self.attempts):
            try:
                response = self.session.post(
                    url,
                    headers=headers,
                    json=payload,
                    params=params,
                    timeout=self.timeout_seconds,
                )
                if response.status_code in {429, 500, 502, 503, 504}:
                    last_error = GriffinError(
                        f"Ensembl VEP REST request failed with HTTP {response.status_code}."
                    )
                elif not response.ok:
                    raise GriffinError(
                        "Ensembl VEP REST request failed with "
                        f"HTTP {response.status_code}: {response.text[:300]}"
                    )
                else:
                    return self._ensure_record_list(response.json())
            except requests.Timeout:
                last_error = GriffinError(
                    "Ensembl VEP REST request timed out. Rerun with --resume after connectivity "
                    "is restored."
                )
            except requests.RequestException as exc:
                last_error = GriffinError(f"Ensembl VEP REST request failed: {exc}")
            if attempt < self.attempts - 1:
                time.sleep(0.5 * (2**attempt))
        assert last_error is not None
        raise last_error

    def _parse_response(
        self,
        variants: list[VariantRecord],
        raw_records: list[dict[str, Any]],
        raw_path: Path | None,
        cache_key: str,
    ) -> list[AnnotatedVariant]:
        if len(raw_records) != len(variants):
            raise GriffinError(
                "Ensembl VEP REST returned an unexpected number of records. "
                "No annotations were fabricated."
            )
        timestamp = datetime.now(timezone.utc).isoformat()
        annotations: list[AnnotatedVariant] = []
        for variant, raw_record in zip(variants, raw_records, strict=True):
            transcripts = raw_record.get("transcript_consequences") or []
            if not transcripts:
                raise GriffinError(
                    f"Ensembl VEP returned no transcript consequences for {variant.variant_id}."
                )
            selected, reason = self._select_transcript(transcripts)
            consequence_terms = selected.get("consequence_terms") or []
            consequence = ",".join(consequence_terms) if consequence_terms else "unknown"
            amino_acids = self._as_optional_str(selected.get("amino_acids"))
            reference_aa, alternate_aa = self._split_amino_acids(amino_acids)
            impact = self._as_optional_str(selected.get("impact")) or raw_record.get(
                "most_severe_consequence", "MODIFIER"
            )
            impact = impact if impact in IMPACT_SCORES else str(impact).upper()
            hgvsp = self._as_optional_str(selected.get("hgvsp"))
            annotations.append(
                AnnotatedVariant(
                    **model_to_dict(variant),
                    source_variant_id=variant.variant_id,
                    assembly=self.genome_assembly,
                    gene=self._as_optional_str(selected.get("gene_symbol"))
                    or self._as_optional_str(raw_record.get("gene_symbol"))
                    or "UNKNOWN",
                    gene_id=self._as_optional_str(selected.get("gene_id")),
                    transcript=self._as_optional_str(selected.get("transcript_id")),
                    protein_id=self._as_optional_str(selected.get("protein_id")),
                    coding_dna_change=self._as_optional_str(selected.get("hgvsc")),
                    protein_change=self._protein_change(hgvsp, amino_acids),
                    amino_acid_position=self._as_optional_int(selected.get("protein_start")),
                    reference_amino_acid=reference_aa,
                    alternate_amino_acid=alternate_aa,
                    amino_acids=amino_acids,
                    codons=self._as_optional_str(selected.get("codons")),
                    consequence=consequence,
                    impact=impact,
                    impact_score=IMPACT_SCORES.get(impact, 0.1),
                    canonical_transcript=self._is_truthy(selected.get("canonical")),
                    mane_transcript=bool(selected.get("mane_select") or selected.get("mane")),
                    biotype=self._as_optional_str(selected.get("biotype")),
                    annotation_source="ensembl_vep_rest",
                    vep_version=self._as_optional_str(raw_record.get("vep_version")),
                    retrieval_timestamp=timestamp,
                    raw_response_artifact=str(raw_path) if raw_path else None,
                    transcript_selection_reason=reason,
                    considered_transcripts=[
                        self._transcript_summary(transcript) for transcript in transcripts
                    ],
                    raw_output={
                        "cache_key": cache_key,
                        "selected_transcript": selected,
                        "input": raw_record.get("input"),
                        "most_severe_consequence": raw_record.get("most_severe_consequence"),
                    },
                )
            )
        return annotations

    def _select_transcript(self, transcripts: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
        ordered = sorted(transcripts, key=self._transcript_sort_key)
        for transcript in ordered:
            if transcript.get("mane_select"):
                return transcript, "mane_select"
        for transcript in ordered:
            if (
                self._is_truthy(transcript.get("canonical"))
                and transcript.get("biotype") == "protein_coding"
            ):
                return transcript, "canonical_protein_coding"
        for transcript in ordered:
            if transcript.get("biotype") == "protein_coding" and self._has_protein_consequence(
                transcript
            ):
                return transcript, "protein_coding_with_protein_consequence"
        return ordered[0], "deterministic_fallback"

    def _transcript_sort_key(self, transcript: dict[str, Any]) -> tuple[str, str, str]:
        return (
            self._as_optional_str(transcript.get("gene_symbol")) or "",
            self._as_optional_str(transcript.get("transcript_id")) or "",
            self._as_optional_str(transcript.get("protein_id")) or "",
        )

    def _has_protein_consequence(self, transcript: dict[str, Any]) -> bool:
        return bool(
            transcript.get("protein_id")
            and (transcript.get("protein_start") or transcript.get("amino_acids"))
        )

    def _transcript_summary(self, transcript: dict[str, Any]) -> dict[str, Any]:
        return {
            "transcript_id": self._as_optional_str(transcript.get("transcript_id")),
            "gene_symbol": self._as_optional_str(transcript.get("gene_symbol")),
            "gene_id": self._as_optional_str(transcript.get("gene_id")),
            "protein_id": self._as_optional_str(transcript.get("protein_id")),
            "canonical": self._is_truthy(transcript.get("canonical")),
            "mane_select": self._as_optional_str(transcript.get("mane_select")),
            "biotype": self._as_optional_str(transcript.get("biotype")),
            "consequence_terms": transcript.get("consequence_terms") or [],
            "protein_start": self._as_optional_int(transcript.get("protein_start")),
            "amino_acids": self._as_optional_str(transcript.get("amino_acids")),
            "hgvsc": self._as_optional_str(transcript.get("hgvsc")),
            "hgvsp": self._as_optional_str(transcript.get("hgvsp")),
        }

    def _variant_to_vep_region(self, variant: VariantRecord) -> str:
        chrom = variant.chrom.removeprefix("chr")
        return f"{chrom} {variant.pos} {variant.variant_id} {variant.ref} {variant.alt} . . ."

    def _request_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "canonical": 1,
            "hgvs": 1,
            "numbers": 1,
            "protein": 1,
            "transcript_version": 1,
            "uniprot": 1,
            "variant_class": 1,
        }
        if self.genome_assembly.upper() == "GRCH38":
            params["mane"] = 1
        return params

    def _cache_path(self, cache_key: str) -> Path | None:
        if not self.cache_dir:
            return None
        return self.cache_dir / f"vep_{cache_key}.json"

    def _write_raw_artifact(self, cache_key: str, raw_records: Any) -> Path | None:
        if not self.raw_artifact_dir:
            return None
        self.raw_artifact_dir.mkdir(parents=True, exist_ok=True)
        path = self.raw_artifact_dir / f"vep.raw.{cache_key}.json"
        path.write_text(json.dumps(raw_records, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def _ensure_record_list(self, raw_records: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_records, list):
            raise GriffinError("Ensembl VEP REST returned malformed JSON; expected a list.")
        if not all(isinstance(record, dict) for record in raw_records):
            raise GriffinError("Ensembl VEP REST returned malformed records.")
        return raw_records

    def _validate_variants(self, variants: list[VariantRecord]) -> None:
        for variant in variants:
            if not variant.chrom or not variant.pos or not variant.ref or not variant.alt:
                raise GriffinError(f"Unsupported malformed variant: {variant.variant_id}")

    def _base_url_for_assembly(self, assembly: str) -> str:
        normalized = assembly.upper()
        if normalized == "GRCH38":
            return ENSEMBL_REST_GRCH38
        if normalized == "GRCH37":
            return ENSEMBL_REST_GRCH37
        raise GriffinError(
            f"Unsupported genome assembly for Ensembl VEP REST: {assembly}. Use GRCh38 or GRCh37."
        )

    def _mock_annotation(self, variant: VariantRecord) -> AnnotatedVariant:
        gene = variant.info.get("GENE") or (
            "BRAF" if variant.chrom == "7" else "GENE" + variant.chrom
        )
        protein_change = variant.info.get("AA") or ("V600E" if gene == "BRAF" else "p.X1Y")
        impact = variant.info.get("IMPACT") or ("HIGH" if gene == "BRAF" else "MODERATE")
        impact_score = IMPACT_SCORES.get(impact, 0.1)
        return AnnotatedVariant(
            **model_to_dict(variant),
            source_variant_id=variant.variant_id,
            assembly=self.genome_assembly,
            gene=gene,
            transcript=variant.info.get("TRANSCRIPT", "ENSTMOCK000001"),
            protein_change=protein_change,
            amino_acids=protein_change,
            consequence=variant.info.get("CSQ", "missense_variant"),
            impact=impact,
            impact_score=impact_score,
            annotation_source="mock",
            transcript_selection_reason="mock",
            raw_output={"source": "mock", "variant_id": variant.variant_id},
        )

    def _split_amino_acids(self, amino_acids: str | None) -> tuple[str | None, str | None]:
        if not amino_acids or "/" not in amino_acids:
            return amino_acids, None
        ref, alt = amino_acids.split("/", 1)
        return ref or None, alt or None

    def _protein_change(self, hgvsp: str | None, amino_acids: str | None) -> str | None:
        if hgvsp:
            return hgvsp.split(":")[-1]
        return amino_acids

    def _as_optional_str(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value)
        return text if text else None

    def _as_optional_int(self, value: Any) -> int | None:
        if value is None or value == "":
            return None
        return int(value)

    def _is_truthy(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"1", "true", "yes"}
