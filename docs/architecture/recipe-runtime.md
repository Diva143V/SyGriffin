# Recipe Runtime

Griffin's generic runtime validates a recipe DAG, resolves exact skill versions,
and executes stages synchronously in stable declaration order. Usable dependency
states are completed, completed-with-warnings, and resumed; failed, blocked, and
skipped dependencies block their direct dependents.

Successful deterministic, resumable stages persist SHA-256-hashed results and
artifacts plus an atomic checkpoint. Resume validates the checkpoint schema,
run/recipe/stage/skill identities and fingerprints, result hash, output paths,
and artifact hashes before emitting `stage_resumed`. Invalid checkpoints emit
`checkpoint_invalidated` and recompute. Events are JSONL and include run/stage
lifecycle plus checkpoint events. The no-op recipe is the sole migrated recipe.

The runtime remains single-process and synchronous. Griffin's legacy neoantigen
pipeline, canine Recipe 001, American Wetware adaptation, and Pegasus integration
have not started.
