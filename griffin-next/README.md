# Griffin

Griffin is the life-sciences research companion: an AI-native workspace that
turns a biological question into a governed, reproducible computational
experiment.

It is built on the OpenScience workbench and deliberately focused on life
sciences. Griffin combines a researcher-facing workspace with curated skills,
reusable experimental recipes, biological data contracts, review gates, and
complete run provenance.

Griffin is for research use. It does not provide diagnoses, treatment
recommendations, patient-specific medical advice, or clinically validated
results. Every clinically adjacent output must be independently reviewed and
validated by qualified experts.

## What makes Griffin different

OpenScience is a broad scientific workbench. Griffin is a life-sciences-native
research system. It is opinionated about biological inputs, reference assets,
tool versions, evidence, uncertainty, and the records needed to replay a result.

A Griffin run records input hashes, reference assemblies and databases,
parameters, tool and model versions, artifacts, warnings, review decisions, and
scientific limitations. The agent may coordinate work, but it must never
fabricate a biological result when required data or a validated method is absent.

## Initial research domains

- Genomics, variant interpretation, and cancer research
- Transcriptomics, single-cell, spatial biology, and multi-omics
- Proteomics, metabolomics, immunology, and molecular biology
- Drug discovery, pharmacogenomics, and systems biology
- Literature evidence, study design, protocol development, and scientific writing

The first validated flagship recipe is canine neoantigen discovery. It requires
explicit sample metadata, genome assembly, tumor/normal context, DLA alleles,
and review checkpoints before any candidate report can be produced.

## Skill governance

Griffin catalogs compatible capabilities from OpenScience, AIPOCH Medical
Research Skills, and ClawBio. An imported skill is not automatically trusted:
it must declare provenance, license, domain, input/output contracts, required
permissions, validation level, and clinical-risk classification before it can be
enabled in a reproducible recipe.

See [the Griffin foundation architecture](docs/griffin-foundation.md) for the
product boundary and implementation milestones.

## Development

This staged rebuild uses Bun 1.3 or later.

```bash
bun install
bun dev
```

## Attribution

This project is derived from OpenScience under Apache-2.0. See [LICENSE](LICENSE)
and [NOTICE](NOTICE). Third-party skill sources retain their respective licenses
and provenance.
