---
name: model-evaluation
description: >
  This skill should be used when the user asks to "evaluate this model", "do error analysis",
  "build an eval set", "which metric should I use", "slice the results", "why is the model
  failing", "compare model quality", "evaluate an LLM", or wants help with NLP metrics,
  ranking metrics, calibration, eval dataset construction, or failure-mode analysis.
metadata:
  version: "0.2.0"
---

# Model evaluation & error analysis

Default posture: the aggregate metric is hiding something, the eval set has problems, and the most valuable output is a ranked failure-mode list with counts — not one number.

## The iron laws

```
NO TRUSTED NUMBER FROM AN UNAUDITED EVAL SET
NO SHIP DECISION FROM AN AGGREGATE ALONE — SLICE AND FLIP-CHECK
EVERY REPORTED METRIC CARRIES A CI
```

Given predictions/data files → compute in code (pandas/sklearn/scipy), don't estimate.

## Workflow

1. **Audit the eval set first**: leakage vs training data (exact + near-dup — MinHash/embeddings for text), label error rate (sample 50; 8% label noise makes sub-8% model differences unresolvable), distribution match to production, staleness.
2. **Metrics match the decision**: aggregate → which ships; slices → safe to ship; calibration → can consumers use the scores. Most asks need all three.
3. **Slice before averaging**: input length, language/locale, user tenure (new vs established — critical for behavioral), head vs tail classes, source, time. Wins-on-average + loses-on-new-users = usually a worse product.
4. **Structured error analysis**: 50-100 errors stratified by slice; taxonomy built bottom-up from the errors; output = failure modes ranked by frequency × severity with 2-3 examples + hypothesized cause each. This drives the roadmap more than any metric.
5. **Uncertainty**: bootstrap CIs on everything. Overlapping CIs = "tied", not "B wins".

## Metric defaults

- **Imbalanced binary**: PR-AUC over ROC-AUC; precision at the product's operating recall. Accuracy without base rate = banned.
- **Ranking/retrieval**: NDCG@k / recall@k at the product's k; MRR for single-answer. Logged-session evals need propensity correction.
- **Calibration** (thresholded/numerically-consumed scores): ECE + reliability diagram; per-segment if scores feed segment decisions; recalibrate after every retrain.
- **Generation**: human/LLM-judge primary; ROUGE/BLEU/chrF = regression guards only. Say this when someone proposes shipping on ROUGE deltas.
- **Regression**: MAE + quantile errors alongside RMSE; residuals by slice.

Formulas, edge cases, pitfalls: `references/metrics-guide.md`.

## LLM eval

- Eval set from real traffic + real failures. 200 sharp examples beat 5,000 vague ones.
- **LLM-as-judge controls or it doesn't count**: randomized response order (position bias), rubric not bare score, validated against ~50 human labels, never judging its own family undisclosed.
- Decoding params are part of the model — pinned in eval config; cross-setting comparisons invalid.
- Public benchmarks: assume contamination until shown otherwise; internal held-out data for ship decisions.
- Agentic/multi-step: pass^k, not single-sample pass rate.

## Regression testing models

Model updates = code releases:

- Frozen golden set incl. past incident cases. Any golden regression = blocking, even if aggregates improve.
- Report: aggregate delta + slice deltas + **flip analysis** (correct→incorrect). Net +1% with 8% flips = 3.5% of users newly broken. Surface the trade.

## Output

Eval report: setup (data, metrics, config), headline + CIs, slice table, ranked failure modes with examples, recommendation (ship / ship-with-mitigations / don't) with evidence. Then: failure modes feed `ml-iterate`; eval-driven experiments get logged via `ml-experiment-journal`.

## Pipeline integration

Append completed gates to `ml/gates.json`: `eval_audit` (step 1 done), `slice_analysis`, `seed_variance` (when variance was quantified), `flip_analysis` + `golden_set` (regression testing), `calibration` (when checked). Save the eval report to `ml/evals/<model>-<date>.md` — `ml-ship` reads the ledger and links the report in the model card. Surface ACTIVE notes from `ml/notes/datasets.md` for any dataset used.
