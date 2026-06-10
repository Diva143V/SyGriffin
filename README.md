# Griffin CLI

Griffin is a CLI-first research engine for reproducible neoantigen candidate discovery. It takes a VCF, HLA alleles, and cancer type metadata, then produces ranked candidate tables, structured evidence artifacts, a run manifest, and a Markdown report.

Research Use Only: Griffin is a computational research acceleration tool. It does not provide clinical diagnosis, treatment recommendations, medical advice, or validated vaccine candidates. All candidates require independent wet-lab validation and expert review.

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Initialize Project

```bash
python -m griffin init
python -m griffin doctor
```

## Validate Input

```bash
python -m griffin validate-input --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma
```

## Demo/Mock Run

Mock mode is explicit and opt-in. Use it only for demos and tests:

```bash
python -m griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001 --mock
```

Mock outputs are deterministic and are clearly marked in the manifest, evidence records, and report.

## Real Run

```bash
python -m griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001
```

Real runs require a configured MHC backend, currently MHCflurry. If no real predictor is available, Griffin fails clearly instead of falling back to mock predictions.

```bash
pip install mhcflurry
mhcflurry-downloads fetch
```

## Optional Local LLM With Ollama

LLM summarization is optional. Griffin works without any LLM by using deterministic report text.

```bash
ollama pull phi3
ollama serve
```

Then:

```bash
python -m griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001 --mock --use-llm --llm-provider ollama --ollama-model phi3
```

Phi-3 is used only for local report/evidence summarization of already retrieved structured evidence records. Griffin must not use Ollama to invent PMIDs, titles, years, trial IDs, genes, variants, or clinical claims.

## Evidence Configuration

If PubMed E-utilities are used, configure:

```bash
export NCBI_EMAIL=you@example.org
export NCBI_API_KEY=
```

When evidence APIs are unavailable in non-mock mode, Griffin does not fabricate evidence records. It writes an empty evidence list and reports that the evidence score was computed as 0.0 or unavailable.

## Output Structure

Each run writes:

```text
runs/<sample-id>/
  manifest.json
  run_manifest.json
  config.resolved.yaml
  report.md
  candidates.csv
  candidates.json
  evidence.json
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

## Commands

```bash
python -m griffin init
python -m griffin doctor
python -m griffin validate-input --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma
python -m griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001 --mock
python -m griffin resume --run-dir runs/demo-001
python -m griffin report --run-dir runs/demo-001 --pdf
python -m griffin version
```

## Tests and Quality

```bash
pytest -q
ruff check .
ruff format .
mypy griffin
```
