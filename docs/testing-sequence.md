# Testing Sequence — Runbook

The ordered procedure to take one model from "untested" to "published." Follow top to bottom. Each phase produces an artifact; nothing is scored until the artifact exists.

Ordering rationale: cheap/fast and contamination-resistant checks first, so a model that's broken or clearly mis-versioned is caught before spending compute on the long agentic runs. Behavioral benchmarks run before the headline coding benchmarks so behavior isn't an afterthought.

---

## Phase 0 — Pin the target

1. Record exact model ID/version (not a moving alias).
2. Record decoding params: temperature, top-p, max output tokens, and any reasoning/effort/thinking setting. Use the vendor's recommended defaults; if you deviate, document why.
3. Record harness versions and benchmark revisions you'll use.
4. Create `results/data/<model>.json` from `results/SCHEMA.md` and fill the metadata block.

**Artifact:** metadata block committed.

---

## Phase 1 — Smoke check

Confirm the endpoint, auth, and harness actually work and the model is the version you think it is.

1. Run a 5–10 item sample from IFEval and SimpleQA.
2. Eyeball outputs for obvious version mismatch (wrong style, refusals, truncation).
3. Abort and fix if anything looks wrong — do not proceed on a misconfigured target.

**Artifact:** smoke-check note (pass/fail + sample transcript).

---

## Phase 2 — Behavioral suite (run before capability)

Behavior is the easiest thing to lose and the easiest to overlook. Lock it in first.

1. **IFEval** → instruction-following (programmatic, no judge).
2. **MultiChallenge** → multi-turn instruction retention.
3. **Collie** → fine-grained constraints.
4. **SycEval** → answer-stability under pushback. Record as resistance score.
5. **Elephant** → social sycophancy.
6. **XSTest** → over-refusal. Record refusal rate explicitly.
7. **SimpleQA** → record both accuracy **and** confident-wrong rate.

**Artifacts:** per-benchmark raw outputs + dimension scores for Instruction-following, Sycophancy, Over-refusal, and the truthfulness/short-form portion.

---

## Phase 3 — Reasoning

1. **GPQA Diamond**
2. **ARC-AGI-2** (contamination-resistant — weight it)
3. **AIME**
4. **FrontierMath** (ingest if not locally runnable)
5. **Humanity's Last Exam** (ingest if gated)

**Artifact:** reasoning dimension score with per-benchmark breakdown and local-run/ingested flags.

---

## Phase 4 — Truthfulness (long-form) & long context

1. **TruthfulQA**
2. **FActScore** (long-form factual precision)
3. **RULER** at the model's supported context lengths.

**Artifact:** truthfulness (combined with Phase 2 SimpleQA) and long-context dimension scores.

---

## Phase 5 — Tool use / agents

1. **BFCL**
2. **τ-bench**
3. **GAIA** (ingest the validation score if gated)

**Artifact:** tool-use dimension score.

---

## Phase 6 — Agentic coding (most expensive, last)

Run last because it's the costliest and most scaffold-sensitive; you want everything else banked first.

1. **LiveCodeBench** (time-windowed — run the window *after* the model's training cutoff).
2. **Aider polyglot**
3. **Terminal-Bench**
4. **SWE-Bench Verified**
5. **SWE-Bench Pro**

Fix the agent scaffold/version across models so coding scores stay comparable.

**Artifact:** coding dimension score with per-benchmark breakdown.

---

## Phase 7 — Holistic cross-check

1. Ingest **LiveBench** (snapshot date).
2. Ingest **LMArena** with **style control on** (snapshot date).
3. Compare against the computed composite. A large divergence is a flag to investigate (contamination, harness bug, saturation), not something to average away.

**Artifact:** cross-check note.

---

## Phase 8 — Score & review

1. Normalize every benchmark to 0–100 (invert behavioral rates so higher = better).
2. Compute dimension means, then the weighted composite using `results/weights.json`.
3. Anomaly review: saturation (≈everyone ≥95), refusal spikes, confident-wrong outliers, ingested-vs-local divergence.
4. Surface separately on the scoreboard: confident-wrong rate, refusal rate, local-run vs. ingested split.

**Artifact:** completed `results/data/<model>.json`.

---

## Phase 9 — Publish

1. Add/refresh the model's row in `results/scoreboard.md`.
2. Commit raw artifacts (or links) per the reproducibility record.
3. Open a PR; a second operator spot-checks one dimension before merge.
4. Merge = published. Git history is the audit trail.

**Artifact:** merged PR.

---

## Operator checklist (per model)

- [ ] Phase 0 metadata pinned
- [ ] Phase 1 smoke check passed
- [ ] Phase 2 behavioral suite complete
- [ ] Phase 3 reasoning complete
- [ ] Phase 4 truthfulness + long context complete
- [ ] Phase 5 tool use complete
- [ ] Phase 6 coding complete
- [ ] Phase 7 cross-check recorded
- [ ] Phase 8 scored + anomaly-reviewed
- [ ] Phase 9 published via PR
