# Skill and Recipe Foundation

A skill is a narrow, versioned callable capability with an explicit manifest.
A recipe is a versioned declaration of stages that reference exact skill
versions. Agents may coordinate future work; skills execute deterministic work.

Milestone 1 adds contracts, safe YAML loaders, registries, JSON Schemas, and a
no-op fixture. It does not add recipe execution, DAG scheduling, CLI commands,
or migrate the existing neoantigen pipeline; those begin in Milestone 2 and 3.
