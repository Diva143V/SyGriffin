# Griffin Project Context

## Current Branch

griffin-cli-mvp

## Latest Commit

Use `git log -1 --oneline` for the exact current commit.

Last completed pushed milestone: `0d2323e Update Griffin scientific MVP status`.

## Current Status

Scientific MVP in progress

## Product Goal

Griffin is a CLI-first, Research-Use-Only computational research tool that takes a VCF
file, HLA alleles, and cancer type metadata, then produces ranked neoantigen candidates,
evidence records, reproducible manifests, and scientific reports.

## Research Use Only Boundary

Griffin does not provide diagnosis, treatment recommendations, medical advice, patient
eligibility, clinically validated vaccine claims, or therapeutic actionability. All outputs
must be described as computational prioritization for research follow-up and require
independent wet-lab validation and expert review.

## Current Architecture

The project is a Typer-based Python CLI with deterministic core modules, agent
orchestration, external integration adapters, pipeline checkpointing, JSON/CSV artifacts,
and Markdown report generation.

## Agent Architecture

Current implemented agents:

- Mutation Agent
- Neoantigen Agent
- Evidence Agent
- Research Lead Agent
- Report Agent

Required Scientific MVP agents still to add or formalize:

- Intake Agent
- Critic Agent
- Safety Agent

## Current CLI Commands

- `python -m griffin init`
- `python -m griffin doctor`
- `python -m griffin validate-input`
- `python -m griffin run`
- `python -m griffin resume`
- `python -m griffin report`
- `python -m griffin version`

## Current Integrations

| Integration | Status | Notes |
|---|---|---|
| MHCflurry | Partial | Adapter exists; unavailable in current Python 3.14 environment. |
| Deterministic mock MHC | Working | Explicit `--mock` only. |
| Ensembl VEP REST | Partial/mock | Client path exists; real Scientific MVP integration remains. |
| PubMed E-utilities | Partial/mock | Mock records are visibly synthetic; real retrieval remains. |
| ClinicalTrials.gov | Partial/mock | Mock records are visibly synthetic; real retrieval remains. |
| Ollama | Optional | Local summarizer adapter exists with reachability detection. |

## Current Scientific Capabilities

- VCF parsing and validation.
- HLA allele validation.
- Deterministic mock run for demo/testing.
- Candidate ranking with transparent weighted scoring.
- Report generation with Research Use Only language.
- Run manifests, checkpoints, and reproducibility artifacts.
- Candidate-level and manifest-level scientific provenance.

## Current Mock-Only Capabilities

- Variant annotation for current demo outputs.
- Peptide sequence generation for current demo outputs.
- Evidence records for current demo outputs with explicit mock IDs and null real IDs.
- MHC predictions when `--mock` is used.

## Current Non-Mock Capabilities

- Input validation.
- Non-mock run fails clearly if MHCflurry is unavailable.
- Report regeneration from existing artifacts.
- Ollama reachability checks.
- Scientific Python version recommendation in `doctor`.

## Current Outputs

- `candidates.csv`
- `candidates.json`
- `evidence.json`
- `manifest.json`
- `run_manifest.json`
- `report.md`
- `config.resolved.yaml`
- `artifacts/*.json`
- `checkpoints/*.done`

## Current Known Issues

- Real MHCflurry prediction is blocked by unavailable scientific environment dependencies.
- Real VEP annotation is not complete.
- Real PubMed retrieval is not complete.
- Real ClinicalTrials.gov retrieval is not complete.
- Python 3.14 works for demo mode but is too new for some scientific dependencies.

## Current Test Status

`python -m pytest -q` passes with 19 tests and 1 Pydantic deprecation warning.

## Current Lint / Type Status

`python -m ruff check .` passes.

`python -m mypy griffin` passes.

## Latest Quality Gate Results

- `python -m pytest -q`: 19 passed, 1 warning.
- `python -m ruff check .`: passed.
- `python -m mypy griffin`: passed.

## Recent Changes

- Added `.griffin/` to `.gitignore`.
- Added `types-requests` to development dependencies.
- Wrapped long lines called out by Ruff.
- Guarded optional MHC binding percentile before constructing scored candidates.
- Avoided optional/string reassignment in Evidence Agent query handling.
- Added mock evidence constraints to the Ollama system prompt.
- Verified tests, lint, and type checks pass after cleanup.
- Changed mock PubMed records to use `mock_pubmed_*` IDs, null PMIDs, and null URLs.
- Changed mock ClinicalTrials records to use `mock_trial_*` IDs, null NCT IDs, and null URLs.
- Updated reports to state that no real PubMed or ClinicalTrials.gov records were retrieved for mock evidence.
- Added tests that prevent fake PMID/NCT-style mock records from returning.
- Added candidate fields for mock status, predictor name/version, annotation source,
  sequence context source, and evidence source.
- Added `scientific_provenance` to run manifests.
- Added a Scientific Provenance section to generated reports.
- Made unfinished non-mock VEP annotation and traceable peptide generation fail clearly
  instead of fabricating biological outputs.
- Verified tests, lint, and type checks pass after provenance changes.
- Added `docs/SCIENTIFIC_ENV_SETUP.md` with the recommended Windows Python 3.11 setup.
- Added `scientific_python_recommended` and a Python 3.13+ warning to `griffin doctor`.
- Verified tests, lint, and type checks pass after environment setup documentation.
- Added `docs/SCIENTIFIC_MVP_STATUS.md` with the current Scientific MVP readiness state.

## Next 5 Tasks

1. Commit Scientific MVP status document.
2. Add or formalize Critic and Safety Agent outputs.
3. Begin real MHCflurry integration verification in a Python 3.11 environment.
4. Add real Ensembl VEP REST annotation.
5. Add biologically traceable peptide generation.

## Important Commands

```bash
python -m pytest -q
python -m ruff check .
python -m mypy griffin
python -m griffin doctor
python -m griffin validate-input --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma
python -m griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001 --mock
```

## Files to Inspect First

- `Griffin_CLI_Codex_Build_Spec.md`
- `docs/GRIFFIN_CONTEXT.md`
- `docs/SCIENTIFIC_MVP_STATUS.md`
- `griffin/cli.py`
- `griffin/pipeline/runner.py`
- `griffin/core/models.py`
- `griffin/integrations/pubmed_client.py`
- `griffin/integrations/clinicaltrials_client.py`
- `griffin/reports/templates/report.md.j2`
- `tests/test_outputs.py`

## Non-Negotiable Rules

1. Do not fabricate biological outputs in non-mock mode.
2. Do not silently fall back to mock mode.
3. Do not fabricate PMIDs.
4. Do not fabricate NCT IDs.
5. Do not let mock records look real.
6. Do not let Ollama create evidence.
7. Do not infer HLA alleles from public databases.
8. Do not assert cancer type if not provided unless a real validated classifier exists.
9. Do not use clinical recommendation language.
10. Do not build frontend.
11. Do not add CARBON yet.
12. Keep Griffin Research Use Only.
13. Update `docs/GRIFFIN_CONTEXT.md` after every meaningful change.
14. Commit after every logical milestone.
15. Push after every successful quality gate.
