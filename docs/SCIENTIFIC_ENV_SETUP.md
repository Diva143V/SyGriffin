# Griffin Scientific Environment Setup

Griffin demo and mock mode can run on newer Python versions, including Python 3.14, but the
scientific dependency stack should use Python 3.11 for best compatibility.

## Recommended Windows Setup

Use `uv` as the project environment manager:

```powershell
uv sync --python 3.11
uv pip install mhcflurry
uv run mhcflurry-downloads fetch models_class1_pan
uv run mhcflurry-downloads fetch models_class1_presentation
uv run python -m griffin doctor
```

## Development Setup

```powershell
uv sync --python 3.11 --group dev
uv run pytest -q
uv run ruff check .
uv run mypy griffin
```

If an older `.venv` points to a removed Python installation, recreate it with `uv sync --python
3.11 --group dev`. Griffin should not depend on stale interpreter shims.

If Windows or OneDrive keeps the stale `.venv` locked, use a separate uv-managed project
environment:

```powershell
$env:UV_CACHE_DIR = ".uv-cache"
$env:UV_PROJECT_ENVIRONMENT = ".uv-venv"
uv sync --python 3.11 --group dev
uv run pytest -q
uv run ruff check .
uv run mypy griffin
```

## Demo Mode on Newer Python

Python 3.14 can still run the CLI demo path:

```powershell
uv run python -m griffin run `
  --vcf data/examples/tiny.vcf `
  --hla HLA-A*02:01 `
  --cancer-type melanoma `
  --sample-id demo-001 `
  --out runs/demo-001 `
  --genome-assembly GRCh37 `
  --mock
```

Mock mode is for demo/testing only. Mock predictions, mock annotations, mock peptides, and
mock evidence are not scientific evidence.

## MHCflurry Notes on Windows

The default `mhcflurry-downloads fetch` command can attempt older archives whose extracted
filenames contain characters that are invalid on Windows. For the current Griffin MHC-I
affinity path, the verified Windows-safe download is:

```powershell
mhcflurry-downloads fetch models_class1_pan
```

The presentation models can also be fetched for future presentation-aware work:

```powershell
mhcflurry-downloads fetch models_class1_presentation
```

Verified local milestone:

```json
{
  "python": "3.11.9",
  "mhcflurry_available": true,
  "mhcflurry_version": "2.2.1",
  "mhcflurry_downloads_available": true,
  "scientific_mhc_ready": true
}
```

## Non-Mock Scientific Requirements

Non-mock Scientific MVP runs require:

- Python 3.11.
- MHCflurry installed and downloads fetched.
- Real Ensembl VEP REST annotation integration.
- Biologically traceable sequence context for peptide generation.
- `NCBI_EMAIL` configured for PubMed E-utilities.
- PubMed and ClinicalTrials.gov network access.

Griffin must fail clearly rather than fabricate biological outputs when one of these
requirements is unavailable.
