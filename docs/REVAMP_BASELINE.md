# Griffin Revamp Baseline

**Audit date:** 2026-06-21

**Audited branch:** `griffin-cli-mvp`

**Griffin commit:** `a1627d9354dfd73c0cf04562e179ef9b87cce6ff` (`docs: rewrite project readme and gitignore`)

**Reference workflow:** [American Wetware canine-neoantigen-speedrun](https://github.com/american-wetware/canine-neoantigen-speedrun)

**Reference commit:** `3be861fe43ebcae763037c62a3da78e6fa35883b`

This is a documentation-and-attribution baseline for the Griffin recipe-platform
revamp. It intentionally changes no runtime behavior.

## Repository state

- The working tree was clean before the Milestone 0 documentation changes.
- `origin` points to `https://github.com/varshhhy7/Griffin.git`; the audited
  branch was already current with `origin/griffin-cli-mvp`.
- `canine-reference` was added as a read-only remote for the American Wetware
  workflow and pinned at the commit above.
- Griffin is a Python 3.10+ Typer CLI, packaged with `uv` and tested here with
  Python 3.11.9.

## Current package tree

```text
griffin/
  adapters/          # LLM and MHC adapter boundaries
  agents/            # Current pipeline-oriented coordinating agents
  bio/               # VCF, peptide, HLA, normalization, and scoring helpers
  config/            # Settings and defaults
  core/              # Models, manifests, hashes, checkpoints, and logging
  integrations/      # VEP, MHCflurry, PubMed, ClinicalTrials, and LLM clients
  pipeline/          # Current runner, context, and stages
  reports/           # Markdown/PDF reporting and templates
  storage/           # Cache and run-store implementations
  cli.py             # Typer CLI
tests/               # 25 unit/integration-style tests and fixtures
docs/                # Current architecture, boundaries, setup, and MVP status
```

## Existing capabilities retained for migration

- Explicit deterministic mock mode, separate from non-mock execution.
- VCF parsing and HLA validation.
- Ensembl VEP REST integration with deterministic transcript selection, raw
  response artifacts, caching, and typed provenance.
- MHCflurry integration that fails clearly when unavailable.
- Deterministic scoring, manifests, checkpoints, cache/run storage, CSV/JSON
  artifacts, Markdown reports, and optional PDF reports.
- Research Use Only language and guarded Ollama summarization boundaries.

## Known incomplete features and risks

- End-to-end non-mock output is intentionally incomplete because peptide
  context is not yet traceable to a verified protein sequence.
- PubMed and ClinicalTrials.gov clients are still partial/mock; real retrieval
  and evidence provenance need completion.
- Critic and Safety reviews are not implemented as deterministic rule engines.
- The current pipeline is human/HLA-oriented; it has no canine sample-manifest
  contract, GCF_011100685.1 backend, or explicit DLA support policy.
- Run and stage provenance have useful foundations but are not yet
  recipe-neutral, content-addressed stage records.
- The existing Pydantic v1-style configuration emits one Pydantic v2
  deprecation warning during tests.
- The checked development dependency ranges currently resolve to `mypy 2.1.0`
  and `pathspec 1.1.1`; `mypy` aborts during its own import because
  `pathspec._backends.hyperscan` is missing. This is an environment/dependency
  compatibility failure before Griffin sources are checked, not a Griffin type
  diagnostic. No dependency change is included in this milestone.

## Quality-gate results

Commands were run after recreating the ignored local `.venv` with Python 3.11.9
because its previous interpreter path was stale.

| Command | Result |
| --- | --- |
| `uv run pytest -q` | Passed: 25 passed, 1 Pydantic deprecation warning |
| `uv run ruff check .` | Passed: all checks passed |
| `uv run mypy griffin` | Blocked: `ModuleNotFoundError: pathspec._backends.hyperscan` while importing mypy dependencies |
| `uv run python -m griffin doctor` | Passed: Python 3.11.9; write permissions available; MHCflurry and its downloads not installed in this fresh environment |

The MHCflurry readiness result reflects the freshly recreated local development
environment; it does not change the codebase's existing integration status.

## Milestone 0 scope confirmation

No Griffin runtime module, CLI behavior, scientific calculation, or test was
changed. The only changes are baseline, attribution, upstream-license, and
project-context documentation.
