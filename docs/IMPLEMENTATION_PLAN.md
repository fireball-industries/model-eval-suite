# Implementation Plan

Written so a new session can resume with no prior context. Read this top to bottom, then start at the first unchecked task.

---

## Where things stand

**Done (committed):**
- Repo created: `fireball-industries/model-eval-suite` (public).
- `docs/SOW.md` — Statement of Work (scope, methodology, scoring, deliverables, reproducibility).
- `docs/testing-sequence.md` — the 10-phase runbook for evaluating one model.
- `benchmarks/catalog.md` — ~25 benchmarks across 7 dimensions, each with rationale + weakness + source.
- `results/` — schema, versioned weights, data template, empty scoreboard.

**Not done yet:**
- No evaluation harness code exists. The repo is currently documents + scaffold only.
- No model has been run. Scoreboard is empty.
- No automation to compute composites or render the scoreboard from `results/data/*.json`.

**The goal of the next phase:** turn the documents into a working pipeline and publish the first real model row.

---

## Decisions already made (don't relitigate)

- Seven weighted dimensions; weights in `results/weights.json` (`v0.1`).
- Behavioral benchmarks (sycophancy, over-refusal, confident-wrong) are surfaced separately, never hidden in the composite.
- Contamination-resistant benchmarks weighted higher; LiveCodeBench windows must be *after* the model's training cutoff.
- Conciseness is deliberately **not** scored (no honest benchmark) — only described qualitatively.
- Scores normalize to 0–100, higher = better; behavioral rates are pre-inverted.

## Open decisions (resolve before/while building)

1. **Execution strategy per benchmark.** Which do we run locally vs. ingest from upstream leaderboards? Gated ones (FrontierMath, HLE, GAIA) are ingest-only for now. Decide the rest by compute budget.
2. **First model(s) to rate.** Suggested: Claude Opus 4.8 and GLM-5.1 (the comparison that started this). Pick at least one to drive the pipeline end to end.
3. **Harness language/layout.** Proposed: a small Python package under `harness/` that wraps each benchmark's official runner and emits the `results/SCHEMA.md` JSON. Confirm Python; confirm no monorepo constraints.
4. **Secrets handling.** API keys via env vars + a `.env` (git-ignored). Confirm which providers we have keys for.

---

## Build sequence

### Milestone 1 — Repo plumbing
- [ ] Add `.gitignore` (Python, `.env`, `results/artifacts/`, harness caches).
- [ ] Add `harness/README.md` describing the runner contract: input = model config; output = one `results/data/<model>.json`.
- [ ] Add `harness/requirements.txt` (or `pyproject.toml`).
- [ ] Add `.env.example` listing required keys (no real secrets).

### Milestone 2 — Scoring + scoreboard automation (build before running anything)
- [ ] `harness/score.py` — reads a `results/data/*.json`, normalizes, applies `weights.json`, writes back `composite`, `surfaced_metrics`, dimension scores. Validate against `results/SCHEMA.md`.
- [ ] `harness/render_scoreboard.py` — regenerates `results/scoreboard.md` from all `results/data/*.json`. Idempotent.
- [ ] Unit tests with a hand-made fixture record so scoring is verified before any real run.

### Milestone 3 — Behavioral suite first (cheapest, highest-signal-for-this-project)
Per testing-sequence Phase 2. These are the differentiator vs. mainstream leaderboards.
- [ ] Wire IFEval (programmatic, no judge — easiest first).
- [ ] Wire SimpleQA; capture **confident-wrong rate** explicitly.
- [ ] Wire XSTest; capture **refusal rate** explicitly.
- [ ] Wire SycEval + Elephant (need a judge model — pick and pin it).
- [ ] Wire MultiChallenge + Collie.
- [ ] Produce a partial `results/data/<first-model>.json` with the behavioral dimensions filled, run `score.py` + `render_scoreboard.py`, and **publish the first row** (even if other dimensions are null). Proves the pipeline.

### Milestone 4 — Capability dimensions
- [ ] Reasoning: GPQA Diamond, ARC-AGI-2, AIME locally; ingest FrontierMath + HLE.
- [ ] Tool use: BFCL, τ-bench locally; ingest GAIA.
- [ ] Long context: RULER.
- [ ] Truthfulness long-form: TruthfulQA, FActScore.

### Milestone 5 — Agentic coding (most expensive, last)
- [ ] LiveCodeBench (post-cutoff window), Aider polyglot, Terminal-Bench, SWE-Bench Verified, SWE-Bench Pro.
- [ ] Pin one agent scaffold/version and reuse it across models for comparability.

### Milestone 6 — Cross-check + publish
- [ ] Ingest LiveBench and LMArena (style-control on) snapshots.
- [ ] Anomaly review (saturation, contamination, refusal spikes, ingested-vs-local divergence).
- [ ] Open PR; second-operator spot-check one dimension; merge = published.

---

## How to run (target state, once harness exists)

```bash
cd model-eval-suite
cp .env.example .env        # fill in API keys
pip install -r harness/requirements.txt
python -m harness.run --model <model-id> --phase behavioral   # runs a phase
python -m harness.score results/data/<model-id>.json          # compute composite
python -m harness.render_scoreboard                           # refresh scoreboard.md
```

(These commands are the *plan*, not yet implemented — Milestone 1–2 create them.)

---

## Conventions for whoever continues

- Commit messages end with the project's Co-Authored-By trailer.
- Don't force-push (history rewriting is policy-blocked here); fix mistakes with a follow-up commit.
- Leave a benchmark `null` rather than guessing a number — an honest gap beats a fabricated score.
- Every ingested score needs a `source` URL + `snapshot` date and gets flagged in `surfaced_metrics.ingested_fraction`.
- Keep the SOW and this plan in sync when scope changes.

## Known housekeeping
- The root commit subject has a stray leading `@` (here-string artifact). Cosmetic; left as-is because fixing it needs a force-push, which is policy-blocked. Don't bother unless doing an authorized history rewrite.
