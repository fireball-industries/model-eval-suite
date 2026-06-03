# Scoreboard

Composite and per-dimension scores (0–100, higher better). Behavioral rates are pre-inverted to resistance/compliance scores. `Conf-wrong` and `Refusal` are surfaced raw because they're the failure modes a composite hides. Composite uses weights `v0.1` unless noted.

## Composite

| Model | Composite | Code | Reason | Instr | Sycoph | Truth | Tool | Refusal-ok | LongCtx | Conf-wrong↓ | Refusal↓ | Ingested% |
|-----|---------|----|------|-----|------|-----|----|----------|-------|-----------|--------|---------|
| claude-opus-4-8 | 100 | – | – | 100 | – | – | – | 100 | – | – | 0 | 0% |
| glm-5.1 | 100 | – | – | 100 | – | – | – | 100 | – | – | 0 | 0% |

## Cross-checks (not in composite)

| Model | LiveBench | LMArena (style-ctrl) | Snapshot |
|-----|---------|--------------------|--------|
| claude-opus-4-8 | – | – | – |
| glm-5.1 | – | – | – |

## How to read this
- **Composite** is a weighted roll-up — useful for ranking, lossy by design. Always look at the dimensions.
- **Conf-wrong↓** and **Refusal↓**: lower is better; these are the "annoying in use" signals (false confidence, preachiness).
- **Ingested%**: how much of the score came from third-party numbers vs. our own runs. Higher = less reproducible by us.
- Verbosity/conciseness is **not** here — no reliable benchmark exists. See each model's `qualitative` notes.
