# Statement of Work — LLM Evaluation Suite

**Project:** model-eval-suite
**Owner:** Fireball Industries
**Version:** 0.1 (draft)
**Status:** Active

---

## 1. Purpose

Define a repeatable process to rate large language models on both **capability** (can it do the task) and **behavior** (is it usable while doing it), and to publish the results in a transparent, reproducible form.

This exists because mainstream leaderboards optimize what's easy to score — pass/fail correctness and length-biased human preference — and miss the traits that determine whether a model is pleasant and trustworthy to work with: instruction-following, conciseness, calibrated uncertainty, and resistance to sycophancy.

## 2. Scope

### In scope
- A fixed, versioned suite of public benchmarks across seven dimensions (Section 5).
- An ordered testing sequence (the runbook) that any operator can follow to evaluate one model.
- A scoring and weighting model that produces a composite plus per-dimension scores.
- A public results format: structured data + human-readable scoreboard.
- Reproducibility metadata captured for every run.

### Out of scope (v0.1)
- Training or fine-tuning models.
- Private/internal benchmarks or proprietary task sets.
- Real-time or continuous evaluation (runs are point-in-time).
- Cost/latency benchmarking beyond recording vendor-published pricing.

## 3. Objectives & Success Criteria

| Objective | Success criterion |
|---|---|
| Reproducibility | A second operator reproduces a published composite within ±2 points using the recorded metadata. |
| Coverage | All seven dimensions populated for every fully-rated model. |
| Contamination resistance | ≥40% of composite weight comes from time-windowed/refreshed benchmarks. |
| Behavioral signal | Sycophancy, over-refusal, and instruction-following each reported separately, never folded into a single "quality" number. |
| Transparency | Every score traceable to a raw artifact (transcript, harness log, or upstream leaderboard snapshot with date). |

## 4. Methodology

1. **Select** the model and pin its exact version/ID and decoding parameters.
2. **Run** each benchmark in the catalog per the testing sequence, or ingest an authoritative upstream score with a dated snapshot where local execution isn't practical.
3. **Record** raw artifacts and reproducibility metadata.
4. **Score** per-dimension, then compute the weighted composite.
5. **Review** for anomalies (saturation, contamination, refusal spikes).
6. **Publish** to `results/` and update the scoreboard.

### Execution modes
- **Local-run** — we run the harness ourselves (preferred for behavioral benchmarks and anything contamination-sensitive).
- **Ingested** — we record a vendor/third-party published score with source URL and snapshot date (used where the official harness is gated or compute-prohibitive). Ingested scores are flagged as such and excluded from the reproducibility guarantee.

## 5. Benchmark Suite (seven dimensions)

Full detail, sources, and known weaknesses in [`benchmarks/catalog.md`](../benchmarks/catalog.md).

| Dimension | Benchmarks | Default weight |
|---|---|---|
| Agentic coding | SWE-Bench Verified, SWE-Bench Pro, Terminal-Bench, Aider polyglot, LiveCodeBench | 25% |
| Reasoning | GPQA Diamond, ARC-AGI-2, FrontierMath, AIME, Humanity's Last Exam | 20% |
| Instruction-following | IFEval, MultiChallenge, Collie | 15% |
| Sycophancy | SycEval, Elephant | 10% |
| Over-refusal | XSTest | 5% |
| Truthfulness | SimpleQA, TruthfulQA, FActScore | 10% |
| Tool use / agents | BFCL, τ-bench, GAIA | 10% |
| Long context | RULER | 5% |

Holistic cross-checks (not weighted into the composite, reported alongside): **LiveBench** (contamination-resistant dashboard) and **LMArena** (human preference, style-control required).

## 6. Scoring

- Each benchmark is normalized to 0–100 (native percentage, or min-max against a documented reference range for non-percentage metrics).
- **Behavioral benchmarks are directionally normalized** so higher = better behavior (e.g. a sycophancy *rate* is inverted to a resistance score).
- Dimension score = mean of its normalized benchmarks (equal weight within a dimension unless noted in the catalog).
- **Composite** = weighted sum of dimension scores using Section 5 weights.
- **Reported, never hidden:** confident-wrong rate (from SimpleQA), refusal rate (from XSTest), and the local-run vs. ingested split.

Weights are configuration, not doctrine — they live in `results/weights.json` and any published score states which weight set produced it.

## 7. Deliverables

1. This SOW.
2. Benchmark catalog with per-benchmark rationale and weaknesses.
3. Testing-sequence runbook.
4. Results schema (`results/SCHEMA.md`) + machine-readable results (`results/data/*.json`).
5. Public scoreboard (`results/scoreboard.md`).
6. Per-run reproducibility record.

## 8. Reproducibility Record (captured per run)

- Model name + exact version/ID
- Run date (UTC)
- Execution mode (local-run / ingested) per benchmark
- Decoding params (temperature, top-p, max tokens, reasoning/effort setting)
- Harness name + version
- Benchmark revision/date
- Source URL + snapshot date for any ingested score
- Operator + link to raw artifacts

## 9. Publication

Results are published in this public repo. Each model gets a `results/data/<model>.json` record and a row on the scoreboard. Updates are commits; history is the audit trail. Ingested scores are visibly labeled and dated.

## 10. Known Limitations

- **Conciseness/verbosity has no reliable public benchmark.** Reported qualitatively, never scored — substituting a proxy would be dishonest.
- Static benchmarks degrade as they leak into training data; mitigated by weighting toward time-windowed sets, not eliminated.
- Ingested scores inherit the upstream harness's flaws and can't be reproduced from our metadata alone.
- Human-preference signal (LMArena) carries length and confidence bias; included only as a cross-check with style control on.
