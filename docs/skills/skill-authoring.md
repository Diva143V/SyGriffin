# Skill Authoring

Create a YAML `SkillManifest` with a lowercase kebab-case ID, Semantic Version,
explicit execution and permissions, inputs/outputs, provenance requirements,
limitations, mock policy, and failure policy. Use safe YAML only; manifests do
not execute their entrypoints while loading.

Regenerate checked-in schemas with:

```bash
uv run python scripts/generate_manifest_schemas.py
```

The included `griffin/skills/noop/skill.yaml` is an infrastructure example only
and produces no scientific output.
