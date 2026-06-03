# Benchmark Catalog

Every benchmark in the suite: what it measures, why it's in, its known weakness, and where to get it. Weakness is listed for every entry on purpose — a benchmark you can't critique is a benchmark you're trusting blindly.

Columns: **Local-run** = can we run it ourselves with a public harness? **Window** = static (leaks over time) or time-windowed/refreshed (contamination-resistant).

---

## 1. Agentic coding — 25%

### SWE-Bench Verified
- **Measures:** resolving real GitHub issues with a passing test, human-validated subset.
- **Why:** the closest public proxy for "fix a real bug in a real repo."
- **Weakness:** static; high-profile, so contamination risk rises over time. Saturating at the top.
- **Local-run:** yes (SWE-bench harness). **Window:** static.
- **Source:** https://www.swebench.com

### SWE-Bench Pro
- **Measures:** harder, less-saturated repair tasks than Verified.
- **Why:** discriminates top models that have flattened on Verified.
- **Weakness:** newer, smaller ecosystem; still static.
- **Local-run:** yes. **Window:** static.
- **Source:** https://www.swebench.com

### Terminal-Bench
- **Measures:** multi-step tasks in a real shell/agent loop.
- **Why:** captures tool-driven, multi-command work, not single-shot codegen.
- **Weakness:** sensitive to the agent scaffold, not just the model.
- **Local-run:** yes. **Window:** static (versioned).
- **Source:** https://www.tbench.ai

### Aider polyglot
- **Measures:** edits across many languages with strict diff/format compliance.
- **Why:** rewards correct *and* well-formed edits; punishes models that can't follow an edit format.
- **Weakness:** tied to Aider's edit protocol; narrow task style.
- **Local-run:** yes. **Window:** static.
- **Source:** https://aider.chat/docs/leaderboards/

### LiveCodeBench
- **Measures:** competitive-programming problems sampled in time windows after model cutoffs.
- **Why:** contamination-resistant coding signal — the headline reason it's here.
- **Weakness:** competitive-programming style ≠ software engineering.
- **Local-run:** yes. **Window:** time-windowed.
- **Source:** https://livecodebench.github.io

---

## 2. Reasoning — 20%

### GPQA Diamond
- **Measures:** graduate-level science questions resistant to web lookup.
- **Why:** hard, expert-authored, low guess rate.
- **Weakness:** static; multiple-choice allows lucky guesses.
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/idavidrein/gpqa

### ARC-AGI-2
- **Measures:** novel abstraction/pattern induction.
- **Why:** strongly contamination-resistant; tests generalization, not recall.
- **Weakness:** puzzle-domain; arguably not representative of work tasks.
- **Local-run:** yes. **Window:** time-windowed (private eval set).
- **Source:** https://arcprize.org

### FrontierMath
- **Measures:** research-level mathematics.
- **Why:** ceiling-raising; very few models score well.
- **Weakness:** held-out/gated; hard to run locally.
- **Local-run:** no (gated). **Window:** static-but-private.
- **Source:** https://epoch.ai/frontiermath

### AIME
- **Measures:** olympiad-style math.
- **Why:** clean numeric answers, widely comparable.
- **Weakness:** annual sets leak fast; very static.
- **Local-run:** yes. **Window:** static.
- **Source:** https://maa.org (problems) / common eval harnesses

### Humanity's Last Exam (HLE)
- **Measures:** frontier-difficulty questions across many fields.
- **Why:** broad, very hard, discriminating at the top.
- **Weakness:** some questions disputed; partly gated.
- **Local-run:** partial. **Window:** static.
- **Source:** https://lastexam.ai

---

## 3. Instruction-following — 15%

### IFEval
- **Measures:** verifiable instruction compliance (format, length, inclusion/exclusion constraints).
- **Why:** directly scores "did it do what was asked" — programmatically checkable, no judge model.
- **Weakness:** constraints are mechanical; doesn't test nuanced intent.
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/google-research/google-research/tree/master/instruction_following_eval

### MultiChallenge
- **Measures:** holding instructions across multi-turn conversation.
- **Why:** catches drift — models that obey turn 1 and forget by turn 5.
- **Weakness:** judge-model dependent.
- **Local-run:** yes. **Window:** static.
- **Source:** https://scale.com/leaderboard/multichallenge

### Collie
- **Measures:** fine-grained, compositional constraint satisfaction.
- **Why:** harder, more granular than IFEval.
- **Weakness:** synthetic constraints.
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/princeton-nlp/Collie

---

## 4. Sycophancy — 10%

### SycEval
- **Measures:** whether the model changes a correct answer under user pushback.
- **Why:** directly scores fake-agreeing / caving to the user.
- **Weakness:** scenario-based; sensitive to prompt phrasing.
- **Local-run:** yes. **Window:** static.
- **Source:** https://arxiv.org/abs/2502.08177
- **Note:** reported as a *resistance* score (higher = better) per SOW §6.

### Elephant
- **Measures:** social sycophancy — flattery, excessive validation, telling the user what they want to hear.
- **Why:** captures the "you're absolutely right" reflex specifically.
- **Weakness:** newer; judge-dependent.
- **Local-run:** yes. **Window:** static.
- **Source:** https://arxiv.org/abs/2505.13995

---

## 5. Over-refusal — 5%

### XSTest
- **Measures:** refusal/moralizing on benign prompts that superficially resemble unsafe ones.
- **Why:** scores preachiness and unnecessary refusal.
- **Weakness:** small set; targets a specific failure shape.
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/paul-rottger/xstest
- **Note:** reported as a refusal rate *and* folded into the dimension as a non-refusal score.

---

## 6. Truthfulness — 10%

### SimpleQA
- **Measures:** short factual questions; critically, scores confident-wrong vs. abstention.
- **Why:** quantifies false confidence — stating guesses as facts.
- **Weakness:** short-form facts only; not long-form factuality.
- **Local-run:** yes. **Window:** static.
- **Source:** https://openai.com/index/introducing-simpleqa/
- **Note:** confident-wrong rate is surfaced separately on the scoreboard, not just absorbed into the score.

### TruthfulQA
- **Measures:** resistance to popular misconceptions.
- **Why:** classic truthfulness signal.
- **Weakness:** older, partially contaminated.
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/sylinrl/TruthfulQA

### FActScore
- **Measures:** factual precision of long-form generations.
- **Why:** complements SimpleQA's short-form with long-form factuality.
- **Weakness:** requires a retrieval/judge pipeline; costlier.
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/shmsw25/FActScore

---

## 7. Tool use / agents — 10%

### BFCL (Berkeley Function-Calling Leaderboard)
- **Measures:** correctness of function/tool calls, including multi-step and parallel.
- **Why:** standard for tool-call accuracy.
- **Weakness:** synthetic APIs; format-sensitive.
- **Local-run:** yes. **Window:** versioned (updated periodically).
- **Source:** https://gorilla.cs.berkeley.edu/leaderboard.html

### τ-bench (tau-bench)
- **Measures:** agentic tool use in realistic customer-workflow settings with rule-following.
- **Why:** tests sustained, policy-bound tool use, not one-shot calls.
- **Weakness:** narrow domains (retail, airline).
- **Local-run:** yes. **Window:** static.
- **Source:** https://github.com/sierra-research/tau-bench

### GAIA
- **Measures:** multi-step assistant tasks needing tools, browsing, reasoning.
- **Why:** general-assistant capability under realistic task chains.
- **Weakness:** validation set partly gated; scaffold-sensitive.
- **Local-run:** partial. **Window:** static.
- **Source:** https://huggingface.co/datasets/gaia-benchmark/GAIA

---

## 8. Long context — 5%

### RULER
- **Measures:** retrieval and reasoning at long context lengths.
- **Why:** real long-context test; replaces saturated needle-in-haystack.
- **Weakness:** synthetic tasks; doesn't capture all long-context use.
- **Local-run:** yes. **Window:** static (parametric length).
- **Source:** https://github.com/NVIDIA/RULER

---

## Holistic cross-checks (reported, not weighted)

### LiveBench
- **Measures:** reasoning, coding, math, language, instruction-following — refreshed monthly.
- **Why:** single contamination-resistant dashboard; good sanity check on the composite.
- **Window:** time-windowed.
- **Source:** https://livebench.ai

### LMArena
- **Measures:** human pairwise preference.
- **Why:** the only large-scale "feel" signal — but biased toward length and confidence.
- **Weakness:** length/confidence/sycophancy bias; **use style-control mode only.**
- **Source:** https://lmarena.ai

---

## Deliberately excluded

- **Plain needle-in-a-haystack (NIAH):** saturated; passed by everything. Use RULER.
- **MMLU (vanilla):** heavily contaminated and saturated; low discrimination at the top.
- **Conciseness/verbosity benchmarks:** none reliable exists. Reported qualitatively per SOW §10, never scored.
