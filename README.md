# Griffin CLI

Griffin is a CLI-first research engine for reproducible neoantigen candidate discovery. It takes a VCF, HLA alleles, and cancer type metadata, then produces ranked candidate tables, structured evidence artifacts, a run manifest, and a Markdown report.

Research Use Only: Griffin is a computational research acceleration tool. It does not provide clinical diagnosis, treatment recommendations, or medical advice. All candidates require independent wet-lab validation and expert review.

## Install

```bash
pip install -e ".[dev]"
```

## Quickstart

```bash
griffin init
griffin doctor
griffin run \
  --vcf data/examples/tiny.vcf \
  --hla HLA-A*02:01 \
  --cancer-type melanoma \
  --sample-id demo-001 \
  --out runs/demo-001
```

## Commands

```bash
griffin init
griffin doctor
griffin validate-input --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma
griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001
griffin resume --run-dir runs/demo-001
griffin report --run-dir runs/demo-001 --pdf
griffin version
```

## Output Structure

Each run writes:

```text
runs/<sample-id>/
  run_manifest.json
  config.resolved.yaml
  logs/griffin.log
  inputs/input.vcf
  inputs/input.sha256
  artifacts/*.json
  outputs/candidates.csv
  outputs/candidates.json
  outputs/evidence.json
  outputs/report.md
  checkpoints/*.done
```

## Mock Mode

Griffin defaults to deterministic mock-safe mode for VEP, PubMed, ClinicalTrials.gov, and MHC prediction when local tools or network access are unavailable. Mock predictions are reproducible and useful for development, but they must not be used for scientific conclusions.

To use MHCflurry, install and configure it separately:

```bash
pip install mhcflurry
mhcflurry-downloads fetch
```

If `mhcflurry-predict` is on `PATH`, Griffin will use it. Otherwise it emits an explicit warning and records mock mode in the manifest and report.

## API Keys

Copy `.env.example` to `.env` or export variables:

```bash
export NCBI_EMAIL=you@example.org
export NCBI_API_KEY=
export GRIFFIN_MOCK_MODE=false
```

LLM summarization is optional and not required for the MVP.

## Resume

```bash
griffin resume --run-dir runs/demo-001
```

Completed checkpoints are skipped where possible. If an external API fails, rerun with `resume` after connectivity is restored.

## Tests and Quality

```bash
pytest -q
ruff check .
ruff format .
mypy griffin
```

