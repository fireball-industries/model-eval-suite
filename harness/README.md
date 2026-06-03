# harness — the stdio benchmarking utility

A small Python package that benchmarks an LLM and emits a results record matching
[`../results/SCHEMA.md`](../results/SCHEMA.md). It is a **stdio utility**: every
step reads a results-record JSON and writes one back, so steps compose with pipes
or operate on files in `results/data/`.

## The runner contract

```
input   = a results record (the SCHEMA.md JSON) — partial is fine
output  = the same record, mutated, validated against SCHEMA.md
```

Two I/O modes for every step:

| Invocation | Reads | Writes |
|---|---|---|
| `python -m harness.<step> results/data/<model>.json` | that file | the same file, in place |
| `python -m harness.<step> -` | stdin | stdout |

The `-` (stdin/stdout) mode is the stdio contract: steps chain without touching
disk, e.g. `... | python -m harness.score - | python -m harness.render_scoreboard`.

## Steps

| Step | Module | What it does |
|---|---|---|
| `run` | `harness.run` *(M3+)* | Runs benchmarks against a pinned model, fills `dimensions[*].benchmarks` + `surfaced_metrics`. Produces the record. |
| `score` | `harness.score` | Derives each `dimensions[*].score` (mean of its benchmark scores), `composite` (weighted by `results/weights.json`, renormalized over the dimensions actually present), and `surfaced_metrics.ingested_fraction`. Pure aggregation — no network. |
| `render-scoreboard` | `harness.render_scoreboard` | Regenerates `results/scoreboard.md` from **all** `results/data/*.json`. Idempotent. Takes no record on stdin. |

`python -m harness` (or the `eval-suite` console script) dispatches: `score`,
`render-scoreboard`.

## Conventions baked into the steps

- **Scores are 0–100, higher = better.** Behavioral rates (sycophancy, refusal)
  are inverted to resistance/compliance scores *at ingestion time* (in `run`),
  so by the time a record reaches `score` everything is already higher-better.
- **A `null` benchmark or dimension is an honest gap**, not a zero. `score`
  skips nulls when averaging and renormalizes composite weights over the
  dimensions that have a score — so a partial record (e.g. behavioral-only)
  still gets a composite, computed only over what was measured.
- **`surfaced_metrics` are never hidden.** `confident_wrong_rate` and
  `refusal_rate` are passed through from `run`; `ingested_fraction` is computed
  by `score` as ingested-benchmarks ÷ scored-benchmarks.
- **Every published score states its `weights_version`.**

## Quick start

```bash
python -m harness.score results/data/<model>.json   # aggregate one record
python -m harness.render_scoreboard                  # refresh the scoreboard
pytest                                               # scoring is unit-tested on a fixture
```
