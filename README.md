# model-eval-suite

A reproducible, contamination-aware testing sequence for rating large language models — and a public record of the results.

Most public leaderboards measure correctness (did the test pass) and human preference (which answer was liked). Neither captures how a model actually *behaves* in use: whether it follows instructions, stays concise, admits uncertainty, or caves to the user. This suite combines both — capability benchmarks and behavioral benchmarks — into one ordered protocol with published results.

## New session? Start here

Read [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md). It states what's done, what's next, and the exact tasks to pick up — written so a fresh session can continue without prior context.

## Repository map

| Path | What it is |
|------|------------|
| [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) | Current state + ordered next steps. **Open this to resume work.** |
| [`docs/SOW.md`](docs/SOW.md) | Statement of Work: scope, methodology, scoring, deliverables, reproducibility. |
| [`docs/testing-sequence.md`](docs/testing-sequence.md) | The ordered runbook for evaluating one model end to end (Phases 0–9). |
| [`benchmarks/catalog.md`](benchmarks/catalog.md) | Every benchmark: what it measures, why it's in, its weakness, source link. |
| [`results/SCHEMA.md`](results/SCHEMA.md) | The per-model results JSON schema. |
| [`results/weights.json`](results/weights.json) | Versioned dimension weights for the composite. |
| [`results/data/_template.json`](results/data/_template.json) | Copy this per model run. |
| [`results/scoreboard.md`](results/scoreboard.md) | Public, human-readable scoreboard. |

## Principles

1. **Contamination-aware.** Time-windowed and refreshed benchmarks (LiveBench, LiveCodeBench, ARC-AGI-2) are weighted above static ones, which get trained on over time.
2. **Behavior counts.** Sycophancy, over-refusal, instruction-following, and confident-wrongness are first-class metrics, not afterthoughts.
3. **Reproducible.** Every published result records model version, date, decoding params, harness version, and benchmark revision.
4. **Honest gaps.** Where no good benchmark exists (e.g. conciseness), we say so rather than substitute a proxy.

## The seven dimensions

Coding · Reasoning · Instruction-following · Sycophancy · Over-refusal · Truthfulness · Tool use · Long context — rolled into a weighted composite, with sycophancy, refusal rate, and confident-wrong rate also surfaced raw so the composite can't hide them. Full detail in the [SOW](docs/SOW.md) and [catalog](benchmarks/catalog.md).

## Clone

```bash
git clone https://github.com/fireball-industries/model-eval-suite.git
cd model-eval-suite
```

## Status

Bootstrapping. SOW, benchmark catalog, testing sequence, and results scaffold are committed. No model rated yet — first run pending per the implementation plan.
