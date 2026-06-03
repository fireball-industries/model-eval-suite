# Results Schema

Every rated model gets one `results/data/<model>.json` file matching the structure below. Scores are 0–100, higher = better (behavioral rates are pre-inverted to resistance/compliance scores). Each benchmark records whether it was `local-run` or `ingested`.

```json
{
  "model": "string — exact model ID/version (not a moving alias)",
  "run_date": "YYYY-MM-DD (UTC)",
  "operator": "string",
  "weights_version": "string — which results/weights.json produced the composite",
  "params": {
    "temperature": 0.0,
    "top_p": 1.0,
    "max_output_tokens": 0,
    "reasoning_effort": "string|null"
  },
  "dimensions": {
    "agentic_coding": {
      "score": 0.0,
      "benchmarks": {
        "swe_bench_verified": { "score": 0.0, "mode": "local-run|ingested", "source": "url", "snapshot": "YYYY-MM-DD" },
        "swe_bench_pro":      { "score": 0.0, "mode": "ingested", "source": "url", "snapshot": "YYYY-MM-DD" },
        "terminal_bench":     { "score": 0.0, "mode": "local-run", "source": "url", "snapshot": "YYYY-MM-DD" },
        "aider_polyglot":     { "score": 0.0, "mode": "local-run", "source": "url", "snapshot": "YYYY-MM-DD" },
        "livecodebench":      { "score": 0.0, "mode": "local-run", "source": "url", "snapshot": "YYYY-MM-DD", "window": "post-cutoff window used" }
      }
    },
    "reasoning":             { "score": 0.0, "benchmarks": {} },
    "instruction_following": { "score": 0.0, "benchmarks": {} },
    "sycophancy":            { "score": 0.0, "benchmarks": {} },
    "over_refusal":          { "score": 0.0, "benchmarks": {} },
    "truthfulness":          { "score": 0.0, "benchmarks": {} },
    "tool_use":              { "score": 0.0, "benchmarks": {} },
    "long_context":          { "score": 0.0, "benchmarks": {} }
  },
  "composite": 0.0,
  "surfaced_metrics": {
    "confident_wrong_rate": 0.0,
    "refusal_rate": 0.0,
    "ingested_fraction": 0.0
  },
  "cross_checks": {
    "livebench":  { "score": 0.0, "snapshot": "YYYY-MM-DD", "source": "url" },
    "lmarena":    { "score": 0.0, "style_control": true, "snapshot": "YYYY-MM-DD", "source": "url" }
  },
  "qualitative": {
    "conciseness": "string — verbosity has no reliable benchmark; describe, don't score",
    "notes": "string — anomalies, saturation flags, caveats"
  },
  "artifacts": "url or path to raw transcripts/harness logs"
}
```

## Rules
- `mode: ingested` scores are excluded from the ±2 reproducibility guarantee (SOW §3) and must carry a `source` + `snapshot`.
- `surfaced_metrics` are always populated and shown on the scoreboard — they are never hidden inside a dimension score.
- `composite` must state which `weights_version` produced it.
- Leave a benchmark `null` rather than guessing if it wasn't run; an honest gap beats a fabricated number.
