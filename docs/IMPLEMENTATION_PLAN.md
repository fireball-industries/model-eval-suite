# Implementation Plan

Written so a new session can resume with no prior context. Read this top to bottom, then start at the first unchecked task.

---

## Where things stand

**Done (committed):**
- Docs + scaffold: SOW, testing-sequence, benchmark catalog, schema, weights, template.
- **Milestone 1** — `harness/` Python package, stdio I/O contract, `.gitignore`, `.env.example`, `pyproject.toml`.
- **Milestone 2** — `harness/score.py` (dimension means + renormalized composite + ingested_fraction) and `harness/render_scoreboard.py` (idempotent), unit-tested (`tests/`).
- **Milestone 3 (partial)** — `harness/benchmarks/ifeval.py` and `xstest.py` (verifier engines + select/score CLIs), with tests. Ran both on `claude-opus-4-8` via **agent-run** and published the first scoreboard row (instruction-following + over-refusal). Re-ran both under a neutralized responder wrapper; scores reproduced.
- **Execution model** — `AGENTS.md`: a model-neutral runbook. The host agent (Claude Code, Kilo Code + GLM-5.1, …) is the responder via its own subagents; the harness never calls a model. `agent-run` mode added to SOW/SCHEMA.
- `.beads/` is git-ignored (private tracker, not shipped in this public repo).

**Not done yet:**
- Capability dimensions (reasoning, tool use, long context), full truthfulness, sycophancy, agentic coding — all unmeasured.
- Full-size benchmark runs (current rows are small samples) and IFEval loose-metric + remaining instruction types.
- GLM-5.1 run via Kilo Code (agent-run, host = GLM); bd-lite bootstrap for cross-machine provisioning.

**The goal of the next phase:** widen coverage (more dimensions, full samples) and add the second model (GLM-5.1) via agent-run in its own harness.

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
