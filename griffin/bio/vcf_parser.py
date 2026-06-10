from __future__ import annotations

from pathlib import Path

from griffin.core.exceptions import InvalidVCFError
from griffin.core.models import VariantRecord


def parse_info(info: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    if info in {"", "."}:
        return parsed
    for item in info.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            parsed[key] = value
        else:
            parsed[item] = "true"
    return parsed


def parse_vcf(path: Path) -> list[VariantRecord]:
    if not path.exists():
        raise InvalidVCFError(f"Invalid VCF: file not found: {path}")
    variants: list[VariantRecord] = []
    saw_header = False
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                saw_header = True
                continue
            if line.startswith("#"):
                continue
            if not saw_header:
                raise InvalidVCFError(
                    "Invalid VCF: missing #CHROM header. Please provide a valid VCF v4.x file."
                )
            fields = line.split("\t")
            if len(fields) < 8:
                raise InvalidVCFError(f"Invalid VCF: line {line_no} has fewer than 8 columns.")
            chrom, pos, _id, ref, alts, qual, filt, info = fields[:8]
            try:
                pos_int = int(pos)
            except ValueError as exc:
                raise InvalidVCFError(f"Invalid VCF: line {line_no} has non-integer POS.") from exc
            for alt in alts.split(","):
                variant_id = f"chr{chrom.removeprefix('chr')}:{pos_int}:{ref}:{alt}"
                variants.append(
                    VariantRecord(
                        variant_id=variant_id,
                        chrom=chrom.removeprefix("chr"),
                        pos=pos_int,
                        ref=ref,
                        alt=alt,
                        qual=None if qual == "." else qual,
                        filter=None if filt == "." else filt,
                        info=parse_info(info),
                    )
                )
    if not saw_header:
        raise InvalidVCFError(
            "Invalid VCF: missing #CHROM header. Please provide a valid VCF v4.x file."
        )
    if not variants:
        raise InvalidVCFError("Invalid VCF: no variant records found.")
    return variants
