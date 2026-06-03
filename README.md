# model-eval-suite

**An honest, contamination-aware way to rate large language models — and a public record of the results.**

*A Fireball Industries LLC project.*

---

Most public leaderboards measure two things: correctness (did the test pass) and human preference (which answer was liked). Neither tells you how a model actually *behaves* when you work with it — whether it follows instructions, admits uncertainty, stays on task, or quietly caves the moment you push back.

`model-eval-suite` measures both. It combines **capability** benchmarks (coding, reasoning, math, tool use, long context) with **behavioral** benchmarks (instruction-following, sycophancy, over-refusal, truthfulness) into one ordered protocol, scores them into a weighted composite, and publishes every result with the metadata needed to reproduce it.

## What makes it different

- **Contamination-aware.** Time-windowed and refreshed benchmarks (LiveBench, LiveCodeBench, ARC-AGI-2) are weighted above static ones, which leak into training data over time.
- **Behavior is first-class.** Sycophancy, over-refusal, and confident-wrongness are scored dimensions and surfaced *raw* on the scoreboard — never buried inside a single "quality" number.
- **Honest gaps.** Where no trustworthy benchmark exists (conciseness, for one), we say so and leave it unscored rather than fake a proxy. A `null` is an honest gap, never a zero.
- **Reproducible.** Every published score records the exact model ID, date, decoding params, harness, benchmark revision, and — for any third-party number — its source and snapshot date.

## The eight dimensions

| Dimension | Weight | Benchmarks |
| --- | ---: | --- |
| Agentic coding | 25% | SWE-Bench Verified/Pro, Terminal-Bench, Aider polyglot, LiveCodeBench |
| Reasoning | 20% | GPQA Diamond, ARC-AGI-2, FrontierMath, AIME, HLE |
| Instruction-following | 15% | IFEval, MultiChallenge, Collie |
| Sycophancy | 10% | SycEval, Elephant |
| Truthfulness | 10% | SimpleQA, TruthfulQA, FActScore |
| Tool use / agents | 10% | BFCL, τ-bench, GAIA |
| Over-refusal | 5% | XSTest |
| Long context | 5% | RULER |

Rolled into a weighted composite, with **sycophancy resistance, refusal rate, and confident-wrong rate** also reported raw so the composite can't hide them. Full rationale, sources, and known weaknesses for every benchmark are in the [catalog](benchmarks/catalog.md); weights live in [`results/weights.json`](results/weights.json) and every score states which weight set produced it.

## How a model gets rated

The suite is **model- and harness-neutral**. The model under test is whatever model is hosting the agent that runs the suite — Claude in Claude Code, GLM-5.1 in Kilo Code, and so on. That agent answers benchmark prompts by spawning its own subagents; a small, model-free Python harness selects the prompts and scores the answers. No provider SDKs, no API keys, no vendor lock-in.

```bash
# 1. select a prompt sample (pure data)
python -m harness.benchmarks.ifeval select --input <dataset> --n 25 --out sample.jsonl

# 2. answer the prompts as yourself, via your harness's own subagents  -> responses.jsonl
#    (see AGENTS.md for the exact, model-neutral runbook)

# 3. score + publish (pure verification — no model involved)
python -m harness.benchmarks.ifeval score --sample sample.jsonl --responses responses.jsonl
python -m harness.score        results/data/<model>.json   # dimension scores + composite
python -m harness.render_scoreboard                         # refresh the scoreboard
```

The runbook any agent follows is [`AGENTS.md`](AGENTS.md). The harness I/O contract is in [`harness/README.md`](harness/README.md).

## Results

See the live [**scoreboard**](results/scoreboard.md).

**Status — under construction.** The scoring and scoreboard pipeline is built and unit-tested. The first row, `claude-opus-4-8`, is a **partial, pipeline-proving rating**: instruction-following (IFEval) and over-refusal (XSTest) only, on small agent-run samples. It is explicitly *not* a finished eight-dimension rating — the remaining dimensions and full-size benchmark runs are in progress. Treat early numbers as a demonstration that the machinery works, not as a verdict.

## Repository map

| Path | What it is |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Model-neutral runbook: how any agent runs a benchmark and publishes a row. |
| [`harness/`](harness/) | The stdio benchmarking utility — selection, scoring, scoreboard rendering, benchmark verifiers. |
| [`docs/SOW.md`](docs/SOW.md) | Statement of Work: scope, methodology, scoring, deliverables, reproducibility. |
| [`docs/testing-sequence.md`](docs/testing-sequence.md) | The ordered runbook for evaluating one model end to end (Phases 0–9). |
| [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) | Current build state + ordered next steps. |
| [`benchmarks/catalog.md`](benchmarks/catalog.md) | Every benchmark: what it measures, why it's in, its weakness, source. |
| [`results/SCHEMA.md`](results/SCHEMA.md) | The per-model results JSON schema. |
| [`results/scoreboard.md`](results/scoreboard.md) | Public, human-readable scoreboard. |

## Clone

```bash
git clone https://github.com/fireball-industries/model-eval-suite.git
cd model-eval-suite
```

---

© 2026 **Fireball Industries LLC**. Benchmarks referenced here are the property of their respective authors; see the [catalog](benchmarks/catalog.md) for sources.
