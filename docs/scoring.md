# Scoring

Composite score:

```text
0.40 * binding_score
+ 0.25 * presentation_score
+ 0.20 * mutation_impact_score
+ 0.15 * evidence_score
```

If `binding_score < 0.35`, the composite score is capped at `0.50` so weak binders cannot rank highly because of literature familiarity alone.

