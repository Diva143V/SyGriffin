# American Wetware Canine Neoantigen Workflow Reference

## Reviewed source

- Repository: [american-wetware/canine-neoantigen-speedrun](https://github.com/american-wetware/canine-neoantigen-speedrun)
- Reviewed commit: `3be861fe43ebcae763037c62a3da78e6fa35883b`
- Review date: 2026-06-21
- License: MIT, with an additional Research/Education-Only disclaimer. See
  `THIRD_PARTY_NOTICES.md` and
  `third_party/licenses/american-wetware-canine-neoantigen-speedrun-LICENSE`.

Files reviewed:

- `README.md`
- `LICENSE`
- `skills/neoantigen-pipeline/SKILL.md`
- `skills/neoantigen-pipeline/reference.md`
- `scripts/00_download_data.sh` through `scripts/05_select_targets.py`

The upstream step 06 IVT construct script was deliberately not reviewed for
reuse or incorporated into Griffin's executable scope. Griffin Recipe 001 ends
with safe computational research outputs.

## What the workflow contributes

The reference describes a useful high-level order of operations for a canine
multi-sample workflow: validate VCF/reference inputs, apply an explicit
somatic-filtering heuristic where calls are unfiltered, annotate against the
matching GFF3 assembly, produce peptide/MHC candidates, rank the full genome,
and apply target-list matching as a late annotation layer.

It also identifies useful data contracts and fixtures to recreate independently:

- ENA analysis `ERZ24794450` and the GCF_011100685.1 / UU_Cfam_GSD_1.0
  assembly pairing.
- The need to parse `FORMAT` fields by name and make tumor/normal roles
  explicit.
- Per-variant rejection reasons and AF-pattern heuristic boundaries.
- GFF3 `gene`, `mRNA`, and `CDS` relationships, strand-aware consequence
  calculation, and cached reference retrieval.
- Mutant and wild-type peptide pairing, MHC raw-output retention, transparent
  ranking, and target-list separation from scoring.

These are workflow ideas and validation requirements, not proof that any
scientific output is correct or clinically/veterinarily relevant.

## What Griffin must rewrite

Future Griffin implementations must be typed, versioned skills with validated
inputs/outputs, structured failures, artifacts, provenance, tests, checkpoint
resume, and recipe-level policy enforcement. In particular, Griffin must add:

- Configurable sample manifests instead of sample IDs embedded in code.
- Assembly validation from VCF metadata and reference-resource hashes.
- A policy-driven multi-sample somatic filter that preserves every
  accept/reject decision and warns that heuristics are not validated truth.
- Strand-aware, transcript-explicit annotation that verifies reference amino
  acids and never fabricates sequence context.
- Paired mutant/wild-type peptide artifacts, mutation-position validation, and
  a separate frameshift path.
- DLA-aware prediction that records requested and used allele, predictor/model
  versions, and raw outputs.
- Fully decomposed, deterministic candidate scoring; target-list status is an
  annotation, not an implicit score change.
- Evidence retrieval, critic review, safety review, and recipe-neutral run
  provenance.

## Unsafe behavior intentionally rejected

Griffin will not reproduce these upstream behaviors:

- Silently substituting `HLA-A*02:01` when a requested DLA allele is
  unsupported. Unsupported DLA must fail or be visibly blocked; any surrogate
  analysis requires a separately named experimental policy and approval.
- Hard-coding `C1`–`C8`, including assuming the normal sample from a fixed
  identifier or column position.
- Treating a downloaded file's existence as proof of a successful, correct
  acquisition; Griffin must record source, hash, size, metadata, and assembly.
- Continuing after unavailable MHC prediction by treating unscored outputs as
  a completed scientific result.
- Allowing missing CDS/reference checks, failed API retrieval, or malformed
  sequence context to yield a fabricated biological result.
- Collapsing the full peptide-level ranking into only one row per gene. Griffin
  will preserve full peptide- and variant-level results as well as a
  best-per-gene view.
- Treating target-list membership or LLM-selected targets as evidence of
  biological validity.
- Exposing IVT vaccine/plasmid design in Recipe 001.

## Adapted logic and attribution status

No upstream code has been copied or substantially adapted in Milestone 0.
Accordingly, there are no Griffin files containing derived logic yet. Before
any future adaptation, the implementing file must include attribution comments,
preserve the upstream MIT notice and research/educational disclaimer, and be
listed here with the source file and scientific changes.
