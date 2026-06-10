# Griffin Scientific Environment Setup

Griffin demo and mock mode can run on newer Python versions, including Python 3.14, but the
scientific dependency stack should use Python 3.11 for best compatibility.

## Recommended Windows Setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -e .
pip install mhcflurry
mhcflurry-downloads fetch
python -m griffin doctor
```

## Development Setup

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
python -m mypy griffin
```

## Demo Mode on Newer Python

Python 3.14 can still run the CLI demo path:

```powershell
python -m griffin run `
  --vcf data/examples/tiny.vcf `
  --hla HLA-A*02:01 `
  --cancer-type melanoma `
  --sample-id demo-001 `
  --out runs/demo-001 `
  --mock
```

Mock mode is for demo/testing only. Mock predictions, mock annotations, mock peptides, and
mock evidence are not scientific evidence.

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
