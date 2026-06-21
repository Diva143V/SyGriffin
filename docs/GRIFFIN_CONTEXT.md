# Griffin Project Context

## Current Branch

griffin-cli-mvp

## Latest Commit

Use `git log -1 --oneline` for the exact current commit.

Last completed pushed milestone: `a1627d9 docs: rewrite project readme and gitignore`.

## Current Status

Scientific MVP in progress; recipe-platform revamp Milestone 0 completed locally.

## Product Goal

Griffin is the AI-native computational research engine for Pegasus. It remains independently
executable as a CLI and will evolve from the current pipeline into versioned recipes composed
of validated scientific skills. Its outputs are Research Use Only computational prioritization,
not clinical or veterinary decisions.

## Research Use Only Boundary

Griffin does not provide diagnosis, treatment recommendations, medical advice, patient
eligibility, clinically validated vaccine claims, or therapeutic actionability. All outputs
must be described as computational prioritization for research follow-up and require
independent wet-lab validation and expert review.

## Current Architecture

The project is a Typer-based Python CLI with deterministic core modules, agent
orchestration, external integration adapters, pipeline checkpointing, JSON/CSV artifacts,
Markdown report generation, and `uv`-managed development environments.

## Current Agent Architecture

Current implemented agents:

- Mutation Agent
- Neoantigen Agent
- Evidence Agent
- Research Lead Agent
- Report Agent

Future review responsibilities still to add or formalize:

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
| MHCflurry | Verified in Python 3.11 | MHCflurry 2.2.1 with pan models returns real IC50 output. |
| Deterministic mock MHC | Working | Explicit `--mock` only. |
| Ensembl VEP REST | Implemented, needs live smoke | Real REST client, caching, raw artifacts, parser tests, and deterministic transcript selection are in place. |
| PubMed E-utilities | Partial/mock | Mock records are visibly synthetic; real retrieval remains. |
| ClinicalTrials.gov | Partial/mock | Mock records are visibly synthetic; real retrieval remains. |
| Ollama | Optional | Local summarizer adapter exists with reachability detection. |

## Current Scientific Capabilities

- VCF parsing and validation.
- HLA allele validation.
- Real Ensembl VEP REST annotation client for GRCh38/GRCh37.
- Deterministic transcript selection with MANE, canonical, protein-coding, and stable fallback
  rules.
- Deterministic mock run for demo/testing.
- Candidate ranking with transparent weighted scoring.
- Report generation with Research Use Only language.
- Run manifests, checkpoints, and reproducibility artifacts.
- Candidate-level and manifest-level scientific provenance.

## Current Mock-Only Capabilities

- Peptide sequence generation for current demo outputs.
- Evidence records for current demo outputs with explicit mock IDs and null real IDs.
- MHC predictions when `--mock` is used.

## Current Non-Mock Capabilities

- Input validation.
- Non-mock run fails clearly if MHCflurry is unavailable.
- Real VEP request, parse, cache, and raw artifact path implemented for non-mock annotation.
- Real MHCflurry prediction path verified in the Python 3.11 `.venv`.
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

- Real VEP annotation passed live Ensembl REST smoke tests for the synthetic tiny fixture as
  GRCh37; broader live and edge-case testing remains.
- Real PubMed retrieval is not complete.
- Real ClinicalTrials.gov retrieval is not complete.
- End-to-end non-mock runs still stop at traceable peptide generation to avoid fabricated
  biology.
- Python 3.14 works for demo mode but is too new for some scientific dependencies.
- On Windows, default `mhcflurry-downloads fetch` can fail on legacy archives with invalid
  filename characters; targeted `models_class1_pan` fetch is verified.
- The older `.venv` on this workstation pointed to a stale Python 3.11 interpreter and was
  recreated locally for the 2026-06-21 revamp baseline.
- The Mypy toolchain is constrained to compatible 1.x releases after the prior Mypy 2.1.0 /
  PathSpec 1.1.1 resolution failed before source analysis. See `docs/REVAMP_BASELINE.md`.

## Current Test Status

`uv run pytest -q` passes with 25 tests and 1 Pydantic deprecation warning in the Python 3.11
`.uv-venv` environment.

## Current Lint / Type Status

`uv run ruff check .` passes.

`uv run python -m mypy griffin` passes with Mypy 1.20.2.

## Latest Quality Gate Results

- `python -m pytest -q`: 20 passed, 1 warning.
- `python -m ruff check .`: passed.
- `python -m mypy griffin`: passed.
- `.venv\Scripts\python.exe -m pytest -q`: 20 passed, 1 warning.
- `.venv\Scripts\python.exe -m ruff check .`: passed.
- `.venv\Scripts\python.exe -m mypy griffin`: passed.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run pytest -q`: 20 passed, 1 warning.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run ruff check .`: passed.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run mypy griffin`: passed.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run python -m griffin doctor`: passed; Python 3.11.9,
  MHCflurry not installed in the fresh uv environment yet.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run pytest -q`: 25 passed, 1 warning after VEP client
  implementation.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run ruff check .`: passed after VEP client implementation.
- `UV_PROJECT_ENVIRONMENT=.uv-venv uv run mypy griffin`: passed after VEP client implementation.
- Live VEP smoke, GRCh37 tiny fixture coordinate: returned BRAF `p.Val600Glu` with
  `canonical_protein_coding` transcript selection.
- Live VEP smoke, GRCh38 same coordinate: returned a different locus, confirming the synthetic
  fixture should be run with `--genome-assembly GRCh37`.

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
- Installed Python 3.11.9 and created the local `.venv` scientific environment.
- Installed Griffin dev dependencies and MHCflurry 2.2.1 in `.venv`.
- Fetched MHCflurry `models_class1_pan` and verified real Class I affinity prediction.
- Fixed the MHCflurry adapter to use `predict_to_dataframe` and record real raw output.
- Added `doctor` fields for MHCflurry version, downloads availability, and scientific MHC
  readiness.
- Verified a non-mock CLI smoke test now passes MHC setup and stops at real VEP annotation.
- Adopted `uv` as the recommended environment and command runner.
- Added `uv.lock` and a `dev` dependency group for reproducible quality gates.
- Added `.uv-cache/` and `.uv-venv/` to `.gitignore` for local uv state.
- Updated README and scientific environment setup documentation with `uv sync`, `uv run`, and
  locked `.venv` recovery guidance.
- Added real Ensembl VEP REST annotation client with request hashing, cache support, retries,
  raw response artifacts, deterministic transcript selection, and typed provenance fields.
- Added `--genome-assembly` to `griffin run`, defaulting to `GRCh38`.
- Verified live VEP smoke tests: the synthetic `tiny.vcf` coordinate resolves to BRAF
  `p.Val600Glu` with GRCh37 and to a different locus with GRCh38, so examples now pass
  `--genome-assembly GRCh37`.
- Added VEP client tests for MANE selection, cache reuse, empty transcript failure, timeout
  failure, and unsupported assembly failure.

## Next 5 Tasks

1. Add biologically traceable peptide generation.
2. Connect real generated mutant/wild-type peptides to MHCflurry.
3. Add formal Intake Agent output.
4. Add PubMed and ClinicalTrials.gov retrieval.
5. Add Critic and Safety Agent outputs.

## Important Commands

```bash
uv sync --python 3.11 --group dev
uv run pytest -q
uv run ruff check .
uv run mypy griffin
uv run python -m griffin doctor
uv run python -m griffin validate-input --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma
uv run python -m griffin run --vcf data/examples/tiny.vcf --hla HLA-A*02:01 --cancer-type melanoma --sample-id demo-001 --out runs/demo-001 --genome-assembly GRCh37 --mock
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
11. Keep Griffin Research Use Only.
12. Update `docs/GRIFFIN_CONTEXT.md` after every meaningful change.
13. Commit after every logical milestone.
14. Push after every successful quality gate.
