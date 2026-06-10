# Griffin CLI — 10/10 Codex Build Spec

**Project:** Griffin  
**Product:** AI-native CLI tool for personalized cancer vaccine / neoantigen discovery research  
**Mode:** CLI-first MVP, no frontend for now  
**Source PRD:** Griffin Product Requirements Document v1.0  
**Goal:** Build a reproducible command-line research pipeline that takes VCF + HLA alleles + cancer type as input and produces ranked neoantigen candidates, evidence summaries, CSV outputs, JSON run artifacts, and a PDF/Markdown scientific report.

---

## 0. Codex Operating Instructions

Codex must treat this file as the implementation contract.

### Git discipline

The repository already has the user's Git credentials configured. Codex must continuously commit changes using those credentials.

Commit rules:

1. Before starting, run:
   ```bash
   git status
   git branch --show-current
   ```
2. Create a working branch if not already on one:
   ```bash
   git checkout -b griffin-cli-mvp
   ```
   If the branch already exists, switch to it.
3. Commit after every meaningful unit of work:
   - project scaffold
   - dependency setup
   - config system
   - VCF parser
   - VEP integration
   - MHCflurry/pVACseq adapter
   - PubMed evidence module
   - ClinicalTrials module
   - scoring engine
   - report generator
   - CLI commands
   - tests
   - docs
4. Use clear commit messages:
   ```bash
   git add .
   git commit -m "feat(cli): add Griffin Typer command scaffold"
   ```
5. Never commit secrets, API keys, `.env`, raw patient data, or large generated outputs.
6. Add `.env`, `runs/`, `data/private/`, `*.vcf.gz`, generated PDFs, and large artifacts to `.gitignore`.
7. Push only when the implementation reaches a stable checkpoint:
   ```bash
   git push origin griffin-cli-mvp
   ```

---

## 1. Product Reframe

The original PRD describes Griffin as a web-based multi-agent platform with upload, job tracking, and reports. For the first build, remove the frontend completely.

The MVP is now:

> A local/server-side CLI pipeline that runs neoantigen discovery from sequencing inputs and generates reproducible research outputs.

This is better for the first version because:

- faster to build
- easier to validate scientifically
- avoids frontend/backend complexity
- makes it useful for bioinformaticians immediately
- can later become the backend engine behind a web app

The CLI must still preserve the PRD's core value:

> From tumor sequencing data to ranked vaccine candidates in hours, not weeks.

---

## 2. MVP Scope

### In scope

Build a CLI that supports:

1. Project initialization
2. Single-sample run
3. VCF parsing and validation
4. HLA allele input validation
5. Cancer type metadata capture
6. Variant annotation through Ensembl VEP REST API, with a local mock fallback for tests
7. Neoantigen candidate generation using a modular adapter interface
8. MHC binding prediction adapter, initially supporting:
   - MHCflurry if installed
   - mock deterministic predictor if not installed
9. Evidence gathering from:
   - PubMed E-utilities
   - ClinicalTrials.gov API
10. Composite candidate scoring
11. Output generation:
   - `candidates.csv`
   - `candidates.json`
   - `evidence.json`
   - `run_manifest.json`
   - `report.md`
   - optional `report.pdf`
12. Reproducibility logging:
   - tool versions
   - parameters
   - timestamps
   - input file hashes
   - API query metadata
13. Checkpointing and reruns
14. Tests for all core modules
15. Clear README with installation and usage

### Out of scope for CLI MVP

Do not build:

- Next.js frontend
- FastAPI backend
- user accounts
- authentication
- cloud deployment
- Stripe/pricing logic
- multi-user workspaces
- HIPAA workflows
- real patient data support
- clinical decision support
- treatment recommendations
- custom ML model training

---

## 3. Core CLI Experience

The CLI package name should be:

```bash
griffin
```

Use `Typer` for CLI commands.

### 3.1 Main commands

```bash
griffin init
```

Creates local project folders:

```text
.griffin/
  config.yaml
  cache/
  logs/
runs/
data/
  examples/
```

---

```bash
griffin run \
  --vcf data/examples/sample.vcf \
  --hla HLA-A*02:01 \
  --hla HLA-B*07:02 \
  --hla HLA-C*07:02 \
  --cancer-type melanoma \
  --sample-id TCGA-DEMO-001 \
  --out runs/TCGA-DEMO-001
```

Runs the full pipeline.

---

```bash
griffin validate-input \
  --vcf data/examples/sample.vcf \
  --hla HLA-A*02:01 \
  --cancer-type melanoma
```

Validates inputs without running expensive steps.

---

```bash
griffin resume --run-dir runs/TCGA-DEMO-001
```

Resumes from the latest successful checkpoint.

---

```bash
griffin report --run-dir runs/TCGA-DEMO-001 --pdf
```

Regenerates report from existing artifacts.

---

```bash
griffin doctor
```

Checks local environment:

- Python version
- required packages
- optional bioinformatics tools
- internet connectivity
- API availability
- write permissions

---

```bash
griffin version
```

Prints Griffin version, Python version, dependency versions, and installed optional tools.

---

## 4. Target Repository Structure

Codex should create this structure:

```text
griffin/
  pyproject.toml
  README.md
  LICENSE
  .gitignore
  .env.example
  Griffin_CLI_Codex_Build_Spec.md

  griffin/
    __init__.py
    __main__.py
    cli.py

    config/
      __init__.py
      settings.py
      defaults.yaml

    core/
      __init__.py
      models.py
      exceptions.py
      logging.py
      manifest.py
      checkpoints.py
      hashing.py

    pipeline/
      __init__.py
      runner.py
      context.py
      stages.py

    agents/
      __init__.py
      research_lead.py
      mutation_agent.py
      neoantigen_agent.py
      evidence_agent.py
      report_agent.py

    bio/
      __init__.py
      vcf_parser.py
      hla.py
      peptide_generator.py
      scoring.py
      normalization.py

    integrations/
      __init__.py
      vep_client.py
      pubmed_client.py
      clinicaltrials_client.py
      mhcflurry_adapter.py
      pvacseq_adapter.py
      llm_client.py

    reports/
      __init__.py
      markdown_report.py
      pdf_report.py
      templates/
        report.md.j2

    storage/
      __init__.py
      run_store.py
      cache.py

    utils/
      __init__.py
      table.py
      time.py
      retry.py

  tests/
    conftest.py
    test_cli.py
    test_vcf_parser.py
    test_hla.py
    test_scoring.py
    test_manifest.py
    test_report.py
    fixtures/
      tiny.vcf
      mock_vep_response.json
      mock_pubmed_response.json

  data/
    examples/
      README.md
      tiny.vcf

  docs/
    architecture.md
    scoring.md
    validation_plan.md
    scientific_boundaries.md
```

---

## 5. Architecture Design

### 5.1 CLI-first architecture

```text
User / Bioinformatician
        |
        v
 Griffin CLI
        |
        v
 Pipeline Runner
        |
        +--> Mutation Agent
        |       +--> VCF parser
        |       +--> VEP client
        |
        +--> Neoantigen Agent
        |       +--> peptide generator
        |       +--> MHCflurry / pVACseq adapter
        |
        +--> Evidence Agent
        |       +--> PubMed client
        |       +--> ClinicalTrials.gov client
        |       +--> optional LLM summarizer
        |
        +--> Research Lead Agent
        |       +--> candidate prioritization
        |       +--> contradiction checks
        |       +--> confidence explanations
        |
        +--> Report Agent
                +--> Markdown report
                +--> CSV/JSON exports
                +--> optional PDF
```

### 5.2 Important design principle

Do not make the agents fake wrappers.

Use this split:

- **Skills/tools** do deterministic execution.
- **Agents** make research decisions, select candidates for deeper analysis, explain results, and produce structured reasoning.

In code:

- `bio/` and `integrations/` contain deterministic skills.
- `agents/` contains orchestration and interpretation logic.
- `pipeline/runner.py` coordinates the stage order.

---

## 6. Agent Design

### 6.1 Research Lead Agent

Purpose:

Coordinates the scientific workflow and acts as the top-level decision layer.

Responsibilities:

- validate whether enough input data exists
- decide which candidates move to evidence search
- identify suspicious results
- produce final candidate rationale
- flag limitations
- ensure report does not make clinical claims

Inputs:

- mutation list
- neoantigen candidates
- evidence summaries
- scoring outputs

Outputs:

- final ranked candidate set
- rationale per candidate
- limitations section
- confidence labels

Confidence labels:

- `high_research_priority`
- `medium_research_priority`
- `low_research_priority`
- `insufficient_evidence`

---

### 6.2 Mutation Agent

Responsibilities:

- parse VCF
- validate required fields
- normalize variants
- call Ensembl VEP REST API
- annotate consequence type
- estimate functional impact
- identify likely driver relevance if available

Output model:

```json
{
  "variant_id": "chr7:140453136:A:T",
  "chrom": "7",
  "pos": 140453136,
  "ref": "A",
  "alt": "T",
  "gene": "BRAF",
  "transcript": "ENST...",
  "protein_change": "V600E",
  "consequence": "missense_variant",
  "impact": "HIGH",
  "impact_score": 0.91
}
```

---

### 6.3 Neoantigen Agent

Responsibilities:

- generate mutant peptide windows
- support 9-11mer MHC-I peptides in MVP
- optionally support MHC-II later
- run binding prediction through adapter
- filter weak candidates
- produce candidate table

Output model:

```json
{
  "candidate_id": "cand_0001",
  "variant_id": "chr7:140453136:A:T",
  "gene": "BRAF",
  "hla": "HLA-A*02:01",
  "peptide": " mutant peptide ",
  "peptide_length": 9,
  "ic50_nm": 87.2,
  "binding_percentile": 0.42,
  "binding_strength": "strong",
  "presentation_score": 0.71
}
```

---

### 6.4 Evidence Agent

Responsibilities:

- query PubMed for gene, mutation, cancer type, and neoantigen terms
- query ClinicalTrials.gov for relevant active trials
- summarize supporting evidence
- separate direct evidence from indirect evidence
- store citations and URLs in structured JSON

Evidence levels:

- `direct_neoantigen_evidence`
- `mutation_cancer_evidence`
- `gene_pathway_evidence`
- `trial_context`
- `weak_or_no_evidence`

Output model:

```json
{
  "candidate_id": "cand_0001",
  "pubmed": [
    {
      "pmid": "12345678",
      "title": "...",
      "year": 2024,
      "journal": "...",
      "evidence_level": "mutation_cancer_evidence",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    }
  ],
  "clinical_trials": [],
  "summary": "Short evidence summary with no clinical claims.",
  "evidence_score": 0.64
}
```

---

### 6.5 Report Agent

Responsibilities:

- generate a structured scientific report
- include methodology
- include parameters
- include candidate ranking
- include evidence summaries
- include limitations
- include research-use-only disclaimer

Output:

- `report.md`
- optional `report.pdf`

---

## 7. Pipeline Stages

The pipeline must run in this order:

```text
1. Input validation
2. Run directory creation
3. Input hashing
4. VCF parsing
5. Variant annotation
6. Mutation scoring
7. Peptide generation
8. MHC binding prediction
9. Candidate filtering
10. Evidence search for top candidates
11. Composite scoring
12. Research Lead review
13. CSV/JSON export
14. Markdown report generation
15. Optional PDF generation
16. Run manifest finalization
```

Each stage must write a checkpoint:

```text
runs/<sample-id>/checkpoints/
  01_input_validation.done
  02_vcf_parsing.done
  03_variant_annotation.done
  ...
```

Each major stage must also write artifacts:

```text
runs/<sample-id>/artifacts/
  variants.raw.json
  variants.annotated.json
  peptides.generated.json
  mhc_predictions.json
  candidates.scored.json
  evidence.json
  final_candidates.json
```

---

## 8. Scoring Model

The original PRD used:

- MHC Binding Affinity: 35%
- Antigen Presentation: 25%
- Literature Evidence: 25%
- Mutation Impact: 15%

For the CLI MVP, use a stronger scientific default:

| Component | Weight | Why |
|---|---:|---|
| MHC Binding Affinity | 40% | Strong binding is the main computational screen. |
| Antigen Presentation | 25% | Presentation likelihood matters beyond binding. |
| Mutation Impact | 20% | Driver/functional impact improves biological relevance. |
| Evidence Strength | 15% | Literature helps explain, but should not over-favor famous mutations. |

Composite score:

```text
composite_score =
  0.40 * binding_score +
  0.25 * presentation_score +
  0.20 * mutation_impact_score +
  0.15 * evidence_score
```

Normalize each score to 0–1.

### Binding score normalization

Lower IC50 is better.

Suggested mapping:

```text
IC50 <= 50 nM      => 1.00
IC50 <= 150 nM     => 0.85
IC50 <= 500 nM     => 0.65
IC50 <= 1000 nM    => 0.35
IC50 > 1000 nM     => 0.10
```

### Evidence score normalization

Evidence must distinguish quality:

```text
direct neoantigen evidence      => high
mutation+cancer evidence        => medium
same gene/pathway evidence      => low-medium
clinical trial context          => contextual
no relevant evidence            => low
```

Do not allow evidence score alone to push a weak binder to the top.

Rule:

```text
If binding_score < 0.35, cap composite_score at 0.50.
```

---

## 9. Data Models

Use Pydantic models for all structured objects.

Core models:

- `RunConfig`
- `RunManifest`
- `SampleMetadata`
- `VariantRecord`
- `AnnotatedVariant`
- `PeptideCandidate`
- `MHCPrediction`
- `EvidenceRecord`
- `ClinicalTrialRecord`
- `ScoredCandidate`
- `FinalCandidate`
- `ReportSection`

Example:

```python
class RunConfig(BaseModel):
    sample_id: str
    vcf_path: Path
    hla_alleles: list[str]
    cancer_type: str
    output_dir: Path
    top_n_evidence: int = 20
    peptide_lengths: list[int] = [9, 10, 11]
    use_llm: bool = False
    generate_pdf: bool = False
```

---

## 10. Configuration

Support config from:

1. CLI flags
2. `.griffin/config.yaml`
3. environment variables
4. defaults

Precedence:

```text
CLI flags > environment variables > config.yaml > defaults.yaml
```

`.env.example`:

```bash
ANTHROPIC_API_KEY=
NCBI_EMAIL=
NCBI_API_KEY=
GRIFFIN_CACHE_DIR=.griffin/cache
GRIFFIN_LOG_LEVEL=INFO
```

LLM usage must be optional.

If no Anthropic key exists, Griffin should still run with extractive/non-LLM summaries.

---

## 11. External Integrations

### 11.1 Ensembl VEP

Implement:

```python
VEPClient.annotate_variants(variants: list[VariantRecord]) -> list[AnnotatedVariant]
```

Requirements:

- retries with exponential backoff
- batch requests where possible
- cache responses by variant hash
- fail gracefully with actionable error
- provide mock mode for tests

---

### 11.2 PubMed

Implement:

```python
PubMedClient.search(query: str, max_results: int) -> list[PubMedRecord]
```

Query strategy:

For each top candidate, search combinations:

```text
<gene> <protein_change> <cancer_type> neoantigen
<gene> <cancer_type> vaccine
<gene> mutation T cell response
<gene> immunotherapy <cancer_type>
```

Requirements:

- use NCBI email if configured
- cache results
- store query strings in manifest
- avoid over-querying

---

### 11.3 ClinicalTrials.gov

Implement:

```python
ClinicalTrialsClient.search(condition: str, terms: list[str]) -> list[ClinicalTrialRecord]
```

Search terms:

- cancer type
- gene
- neoantigen
- personalized vaccine
- mRNA vaccine

---

### 11.4 MHCflurry Adapter

Implement:

```python
MHCflurryAdapter.predict(peptides, hla_alleles) -> list[MHCPrediction]
```

Behavior:

- detect if `mhcflurry-predict` is installed
- if installed, use it
- if not installed, use deterministic mock predictor with warning
- do not silently pretend mock predictions are real
- report must clearly say when mock mode was used

---

### 11.5 pVACseq Adapter

Prepare interface, but full integration can be Phase 1.5:

```python
PVACseqAdapter.run(vcf_path, hla_alleles, output_dir) -> list[PeptideCandidate]
```

For initial MVP, MHCflurry path is enough.

---

## 12. Report Design

`report.md` must include:

1. Title
2. Research-use-only disclaimer
3. Input summary
4. Methodology
5. Tool versions
6. Candidate ranking table
7. Top candidate deep dives
8. Evidence summary
9. Clinical trial context
10. Limitations
11. Reproducibility manifest
12. Appendix with raw parameters

### Required disclaimer

Every report must include:

```text
Research Use Only: Griffin is a computational research acceleration tool. It does not provide clinical diagnosis, treatment recommendations, or medical advice. All candidates require independent wet-lab validation and expert review.
```

### Candidate table columns

```text
Rank
Candidate ID
Gene
Mutation
HLA
Peptide
IC50 nM
Binding Strength
Presentation Score
Mutation Impact Score
Evidence Score
Composite Score
Confidence Label
```

---

## 13. Output Directory Contract

Each run must produce:

```text
runs/<sample-id>/
  run_manifest.json
  config.resolved.yaml
  logs/
    griffin.log
  inputs/
    input.vcf
    input.sha256
  artifacts/
    variants.raw.json
    variants.annotated.json
    peptides.generated.json
    mhc_predictions.json
    candidates.scored.json
    evidence.json
    final_candidates.json
  outputs/
    candidates.csv
    candidates.json
    evidence.json
    report.md
    report.pdf optional
  checkpoints/
    *.done
```

---

## 14. Error Handling

Errors must be clear and actionable.

Examples:

Invalid VCF:

```text
Invalid VCF: missing #CHROM header. Please provide a valid VCF v4.x file.
```

Invalid HLA:

```text
Invalid HLA allele: HLA-A02:01. Expected format like HLA-A*02:01.
```

Missing optional MHCflurry:

```text
MHCflurry is not installed. Griffin will use deterministic mock predictions. Do not use mock predictions for scientific conclusions.
```

API failure:

```text
VEP API request failed after 3 retries. You can rerun with --resume after connectivity is restored.
```

---

## 15. Testing Requirements

Use `pytest`.

Minimum tests:

- CLI starts
- `griffin doctor` works
- `griffin init` creates expected folders
- VCF parser reads fixture
- invalid VCF fails clearly
- HLA validation accepts valid alleles
- HLA validation rejects invalid alleles
- scoring is deterministic
- binding score normalization works
- weak binders cannot rank too high due to evidence
- report generation includes disclaimer
- manifest includes input hash
- resume skips completed checkpoints

Run tests with:

```bash
pytest -q
```

Add lint/type tooling:

```bash
ruff check .
ruff format .
mypy griffin
```

---

## 16. Scientific Boundaries

Codex must ensure Griffin never says:

- this vaccine will work
- this is clinically recommended
- this is safe for a patient
- this should be used for treatment
- this replaces oncologist/bioinformatician review

Allowed language:

- candidate
- research priority
- computational prediction
- evidence-backed ranking
- requires wet-lab validation
- for research use only

---

## 17. Implementation Order for Codex

Build in this exact order.

### Step 1 — Scaffold

- create `pyproject.toml`
- configure package
- add Typer CLI
- add README
- add `.gitignore`
- commit

Commit:

```bash
git add . && git commit -m "chore: scaffold Griffin CLI project"
```

---

### Step 2 — Config and logging

- settings loader
- default config
- `.env.example`
- structured logging
- commit

Commit:

```bash
git add . && git commit -m "feat(config): add settings and logging"
```

---

### Step 3 — Core models

- Pydantic models
- exceptions
- run manifest
- hashing utilities
- commit

Commit:

```bash
git add . && git commit -m "feat(core): add data models and run manifest"
```

---

### Step 4 — CLI commands

- `init`
- `doctor`
- `validate-input`
- `run`
- `resume`
- `report`
- commit

Commit:

```bash
git add . && git commit -m "feat(cli): add core Griffin commands"
```

---

### Step 5 — VCF + HLA

- VCF parser
- HLA validator
- tiny fixture
- tests
- commit

Commit:

```bash
git add . && git commit -m "feat(bio): add VCF parser and HLA validation"
```

---

### Step 6 — Mutation Agent

- VEP client
- mock response
- annotation models
- mutation scoring
- commit

Commit:

```bash
git add . && git commit -m "feat(agent): add mutation annotation pipeline"
```

---

### Step 7 — Neoantigen Agent

- peptide generation
- MHCflurry adapter
- deterministic mock predictor
- candidate filtering
- commit

Commit:

```bash
git add . && git commit -m "feat(agent): add neoantigen candidate generation"
```

---

### Step 8 — Evidence Agent

- PubMed client
- ClinicalTrials client
- evidence scoring
- caching
- commit

Commit:

```bash
git add . && git commit -m "feat(agent): add evidence gathering"
```

---

### Step 9 — Scoring + Research Lead

- composite scoring
- confidence labels
- final ranking
- limitation detection
- commit

Commit:

```bash
git add . && git commit -m "feat(scoring): add research lead ranking logic"
```

---

### Step 10 — Reports

- Markdown report
- CSV/JSON exports
- optional PDF
- commit

Commit:

```bash
git add . && git commit -m "feat(report): add research report generation"
```

---

### Step 11 — End-to-end pipeline

- pipeline runner
- checkpoints
- resume
- output directory contract
- tests
- commit

Commit:

```bash
git add . && git commit -m "feat(pipeline): add end-to-end CLI workflow"
```

---

### Step 12 — Polish

- README usage
- docs
- validation plan
- architecture doc
- final tests
- commit

Commit:

```bash
git add . && git commit -m "docs: add Griffin CLI usage and validation plan"
```

---

## 18. README Requirements

README must include:

- what Griffin CLI is
- research-use-only disclaimer
- installation
- quickstart
- example command
- output structure
- mock mode warning
- how to install MHCflurry
- how to configure API keys
- how to resume failed runs
- how to run tests

Example quickstart:

```bash
pip install -e .
griffin init
griffin doctor
griffin run \
  --vcf data/examples/tiny.vcf \
  --hla HLA-A*02:01 \
  --cancer-type melanoma \
  --sample-id demo-001 \
  --out runs/demo-001
```

---

## 19. Definition of Done

The CLI MVP is complete when:

1. `pip install -e .` works
2. `griffin doctor` works
3. `griffin init` works
4. `griffin validate-input` works on fixture VCF
5. `griffin run` completes end-to-end using mock-safe mode
6. outputs are created exactly as specified
7. `report.md` is generated
8. `candidates.csv` is generated
9. `run_manifest.json` contains hashes, versions, and parameters
10. `pytest -q` passes
11. `ruff check .` passes
12. README gives copy-paste usage
13. all changes are committed to git in logical commits

---

## 20. Future Upgrade Path

After CLI MVP is stable:

### Phase 1.5

- real MHCflurry installation support
- pVACseq full adapter
- PDF polish
- TCGA sample benchmark

### Phase 2

- RNA-seq expression-aware ranking
- batch VCF processing
- stronger validation against published neoantigen studies
- academic lab pilot

### Phase 3

- FastAPI wrapper around the CLI engine
- web dashboard
- authentication
- job queue
- cloud storage

### Phase 4

- HIPAA-ready deployment
- audit trails
- enterprise API
- pharma workflows

---

## Final Instruction to Codex

Build Griffin as a CLI-first scientific research engine, not a web app.

Focus on correctness, reproducibility, transparent scoring, clean reports, and safe scientific boundaries.

Commit continuously to git using the user's already configured credentials.
