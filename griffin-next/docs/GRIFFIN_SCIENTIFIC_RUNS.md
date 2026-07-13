# Griffin Scientific Runs

## Current Milestone

Griffin now has a first-class, persisted scientific run foundation. A run is no
longer only a chat message, terminal command, or collection of output files.
It is a project-scoped research record with validated inputs, parameters,
workflow version, plan, status, progress, logs, outputs, warnings, approvals,
and timestamps.

This is the foundation for job execution, evidence review, comparison,
reproducibility packages, and scientific branches.

## Implemented

- `ResearchRun` schema and project-scoped persistent storage.
- Run states: blocked, awaiting approval, ready, running, completed, failed,
  and cancelled.
- Scientific run API for listing, creating, inspecting, approving, cancelling,
  and retrying runs.
- Versioned RNA-seq differential-expression workflow definition.
- Structured RNA-seq launcher form in the Runs workspace tab.
- SHA-256 checksums for count-matrix and metadata inputs.
- Count-matrix shape validation.
- Exact count-matrix/metadata sample-ID matching.
- Control and treatment presence checks.
- Minimum-replicate validation.
- Batch-column existence and full-confounding detection.
- Inspectable validation results, analysis plan, parameters, logs, warnings,
  and approval state.
- Focused workflow-validation tests.

## Safety Boundary

Approving a validated run changes its state to `ready`. It does not mark the
run as running or completed. Griffin will not claim that DESeq2, pathway
analysis, evidence review, or artifact generation happened until an execution
worker records those events and outputs.

The Runs UI states this boundary directly when a run is ready.

## API

All endpoints are project-scoped through Griffin's existing `directory` query
parameter.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/research-runs/workflows` | List available structured workflows. |
| POST | `/research-runs/validate` | Validate files and parameters without creating a run. |
| GET | `/research-runs` | List runs for the current project. |
| POST | `/research-runs` | Validate and create a persisted run. |
| GET | `/research-runs/:runID` | Inspect one run. |
| POST | `/research-runs/:runID/approve` | Approve a validated plan and mark it ready. |
| POST | `/research-runs/:runID/cancel` | Cancel an active or waiting run. |
| POST | `/research-runs/:runID/retry` | Reset a failed or cancelled run for review. |

## Next Execution Slice

The next implementation should add a local DESeq2 worker that consumes only
approved `ready` runs and records every state transition. It must write command,
environment, stdout/stderr, output paths, checksums, warnings, and provenance
back into the run record.

That worker should produce, at minimum:

- normalized counts;
- differential-expression table;
- PCA data and figure;
- volcano-plot data and figure;
- heatmap data and figure;
- pathway-enrichment results;
- methods text;
- provenance and review records.

The first complete scientific-run milestone is not finished until a researcher
can execute that worker, inspect its results, review the evidence, change a
parameter, and rerun from the GUI.
