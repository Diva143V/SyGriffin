# Griffin Scientific MVP Status

## Overall Status

Scientific MVP partially complete

## What Works in Non-Mock Mode

- CLI startup.
- `doctor`.
- `validate-input`.
- VCF parsing and HLA validation.
- Real Ensembl VEP REST client with deterministic transcript selection, cache support, raw
  response artifacts, and typed annotation provenance.
- Clear failure if MHCflurry is unavailable.
- Real MHCflurry Class I affinity prediction in a Python 3.11 environment.
- `doctor` reports MHCflurry package, version, downloads availability, and scientific MHC
  readiness.
- Clear failure instead of fabricated peptide sequence context when non-mock execution reaches
  the unfinished traceable peptide-generation integration.

## What Still Requires Mock Mode

- Current demo peptide sequence generation.
- Current demo evidence records.
- Current demo MHC predictions without MHCflurry.
- End-to-end candidate/report generation until traceable peptide generation is complete.

## Real Tools Integrated

| Tool | Status | Notes |
|---|---|---|
| MHCflurry | Verified | Python 3.11.9, MHCflurry 2.2.1, pan model downloads, real IC50 output. |
| Ensembl VEP REST | Implemented | Real REST client, caching, raw artifacts, transcript selection, parser tests, and tiny fixture live smoke are in place. |
| PubMed E-utilities | Not complete | Mock records are visibly synthetic and use no fake PMIDs. |
| ClinicalTrials.gov | Not complete | Mock records are visibly synthetic and use no fake NCT IDs. |
| Ollama | Optional | Used only for summaries; mock evidence returns a safe static summary. |

## Agent Status

| Agent | Status | Notes |
|---|---|---|
| Intake Agent | Partial | Validation exists in CLI/pipeline but is not formalized as an agent. |
| Mutation Agent | Partial | Real VEP client exists; broader biological edge cases remain. |
| Neoantigen Agent | Partial | Mock peptide generation exists; traceable sequence context remains. |
| Evidence Agent | Partial | Mock evidence is safe; real retrieval remains. |
| Critic Agent | Not started | Required for Scientific MVP. |
| Safety Agent | Not started | Required for Scientific MVP. |
| Report Agent | Working | Markdown report includes Research Use Only and scientific provenance. |

## Generated Outputs

- `candidates.csv`
- `candidates.json`
- `evidence.json`
- `manifest.json`
- `run_manifest.json`
- `report.md`
- `artifacts/*.json`
- `checkpoints/*.done`

## Benchmark Results

No benchmark suite is implemented yet.

## Scientific Limitations

- Current end-to-end successful runs require `--mock`.
- Mock annotations, peptides, predictions, evidence, and trial records are not scientific evidence.
- Real VEP annotations require Ensembl REST network access and currently support GRCh38 or GRCh37.
- No human proteome/self-homology safety screen is implemented.
- No real PubMed contradiction review is implemented.
- No benchmark establishes clinical validity, and Griffin must not make clinical claims.

## Engineering Limitations

- Python 3.11 is recommended for scientific dependencies; current Python 3.14 is demo-capable
  but may not support MHCflurry cleanly.
- On Windows, default `mhcflurry-downloads fetch` can fail on legacy archives with invalid
  filename characters; `models_class1_pan` was fetched and verified separately.
- Real network integrations need retries, provenance, and caching hardening.
- The Pydantic v1-style config emits a deprecation warning under Pydantic v2.
- `uv` is now the recommended project environment manager. The checked `uv.lock` resolves the
  development stack; MHCflurry still needs to be installed in the active uv environment before
  `doctor` reports scientific MHC readiness.
- The older `.venv` on this workstation points to a stale Python interpreter and can remain
  locked by Windows/OneDrive. Use `.uv-venv` with `UV_PROJECT_ENVIRONMENT` if `.venv` cannot be
  recreated immediately.

## Next Steps After MVP

- Add biologically traceable peptide generation from real protein sequence context.
- Add real PubMed and ClinicalTrials.gov retrieval.
- Add Critic Agent and Safety Agent outputs.
- Add the toy benchmark suite.
