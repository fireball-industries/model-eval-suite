# model-eval-suite

A reproducible, contamination-aware testing sequence for rating large language models — and a public record of the results.

Most public leaderboards measure correctness (did the test pass) and human preference (which answer was liked). Neither captures how a model actually *behaves* in use: whether it follows instructions, stays concise, admits uncertainty, or caves to the user. This suite combines both — capability benchmarks and behavioral benchmarks — into one ordered protocol with published results.

## What's here

- [`docs/SOW.md`](docs/SOW.md) — Statement of Work: scope, methodology, scoring, deliverables.
- [`docs/testing-sequence.md`](docs/testing-sequence.md) — the ordered runbook for evaluating a model end to end.
- [`benchmarks/catalog.md`](benchmarks/catalog.md) — every benchmark in the suite, what it measures, why it's included, and its known weaknesses.
- [`results/`](results/) — published scores, structured data, and the live scoreboard.

## Principles

1. **Contamination-aware.** Time-windowed and refreshed benchmarks (LiveBench, LiveCodeBench, ARC-AGI-2) are weighted above static ones, which get trained on over time.
2. **Behavior counts.** Sycophancy, over-refusal, instruction-following, and confident-wrongness are first-class metrics, not afterthoughts.
3. **Reproducible.** Every published result records model version, date, decoding params, harness version, and benchmark revision.
4. **Honest gaps.** Where no good benchmark exists (e.g. conciseness), we say so rather than substitute a proxy.

## Status

Bootstrapping. Benchmark catalog and protocol defined; first model run pending.
