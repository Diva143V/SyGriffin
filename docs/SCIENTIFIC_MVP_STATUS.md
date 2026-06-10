# Griffin Scientific MVP Status

## Overall Status

Scientific MVP partially complete

## What Works in Non-Mock Mode

- CLI startup.
- `doctor`.
- `validate-input`.
- VCF parsing and HLA validation.
- Clear failure if MHCflurry is unavailable.
- Clear failure instead of fabricated VEP annotation or peptide sequence context when non-mock
  execution reaches those unfinished integrations.

## What Still Requires Mock Mode

- Current demo variant annotation.
- Current demo peptide sequence generation.
- Current demo evidence records.
- Current demo MHC predictions without MHCflurry.
- End-to-end candidate/report generation in the current Python 3.14 environment.

## Real Tools Integrated

| Tool | Status | Notes |
|---|---|---|
| MHCflurry | Partial | Adapter exists; scientific environment setup still required. |
| Ensembl VEP REST | Not complete | Non-mock mode now fails clearly instead of mock-annotating. |
| PubMed E-utilities | Not complete | Mock records are visibly synthetic and use no fake PMIDs. |
| ClinicalTrials.gov | Not complete | Mock records are visibly synthetic and use no fake NCT IDs. |
| Ollama | Optional | Used only for summaries; mock evidence returns a safe static summary. |

## Agent Status

| Agent | Status | Notes |
|---|---|---|
| Intake Agent | Partial | Validation exists in CLI/pipeline but is not formalized as an agent. |
| Mutation Agent | Partial | Mock annotation path exists; real VEP remains. |
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
- No human proteome/self-homology safety screen is implemented.
- No real PubMed contradiction review is implemented.
- No benchmark establishes clinical validity, and Griffin must not make clinical claims.

## Engineering Limitations

- Python 3.11 is recommended for scientific dependencies; current Python 3.14 is demo-capable
  but may not support MHCflurry cleanly.
- Real network integrations need retries, provenance, and caching hardening.
- The Pydantic v1-style config emits a deprecation warning under Pydantic v2.

## Next Steps After MVP

- Complete real MHCflurry prediction verification in Python 3.11.
- Add Ensembl VEP REST annotation.
- Add biologically traceable peptide generation from real protein sequence context.
- Add real PubMed and ClinicalTrials.gov retrieval.
- Add Critic Agent and Safety Agent outputs.
- Add the toy benchmark suite.
