---
name: experiment-design
description: >
  This skill should be used when the user asks to "design an experiment", "plan an ablation",
  "set up an A/B test", "how big a sample do I need", "is this result significant", "design
  an offline evaluation", "compare model variants", or wants help with power analysis, metric
  selection, holdouts, or interpreting experiment results for ML/behavioral systems.
metadata:
  version: "0.2.0"
---

# Experiment design

The statistical conscience of an ML org. Offline (ablations, model comparisons) and online (A/B on behavioral systems). Rigor by default; every shortcut flagged with its risk.

## The iron laws

```
ONE VARIABLE PER ARM
HYPOTHESIS AND SUCCESS CRITERIA WRITTEN BEFORE THE RUN
NO CLAIMED WIN WITHOUT VARIANCE QUANTIFIED
```

Log every experiment via `ml-experiment-journal` before running. When real numbers are given, compute — run the code, don't approximate.

## Classify first

- Offline comparison/ablation → controlled runs, paired eval, seed variance.
- Online product experiment → randomization unit, power, guardrails.
- Result interpretation → audit the design before the numbers; most "significant" results die in the audit.

## Offline experiments

1. **One variable per arm.** Two things changed → comparison dead. Force factorial or sequential.
2. **Seeds before claims**: ≥3 seeds, mean ± std. 0.4% improvement with 0.6% seed std = noise. Single-seed LLM results = provisional, say so.
3. **Paired comparison, identical eval sets**: same examples, preprocessing, decoding. Use paired bootstrap/permutation over examples — far more sensitive than comparing aggregates.
4. **Ablate from the full system down** (leave-one-out); interactions hide in the build-up direction.
5. **Equal tuning budget across arms.** New-method-tuned-a-week vs baseline-at-defaults is the most common false discovery in ML.

## Online A/B — checklist in order, each item can invalidate the rest

1. **Randomization unit**: user-level default. Session/request randomization + user-level outcomes = contamination. Interference (marketplace, social, shared inventory) → cluster or switchback.
2. **One primary metric**, pre-registered, directional. Rest = guardrails or exploratory.
3. **Power before launch**: MDE from baseline variance + traffic. MDE > plausible effect → say so; propose longer duration, CUPED (30-50% variance cut on behavioral metrics), or a more sensitive proxy.
4. **Full weeks (≥1, prefer 2)**; never stop at first significance. Stakeholders will peek → prescribe sequential bounds (mSPRT/group-sequential), don't pretend otherwise.
5. **Guardrails**: latency, errors, retention, revenue-adjacent, with non-inferiority bounds. Engagement win + latency regression = loss.
6. **Delayed/censored outcomes**: respect the maturation window — matured cohorts only. Day-1 conversion comparisons bias toward fast converters.
7. **Feedback-loop treatments** (ranking): long-term holdback (1-5%) to catch cumulative effects offline metrics can't see.

## Interpreting results

- **SRM check first** (chi-square on assignment counts). SRM → test invalid, p-values irrelevant.
- Effect size + CI, not p-value alone. Statistical ≠ practical significance.
- Post-hoc segment wins = hypothesis-generating. Many scans → BH-FDR.
- Wide-CI neutral = "underpowered", not "no effect". Say which.

## Formulas

Power/MDE, CUPED, delta method for ratio metrics, sequential bounds, paired bootstrap, seed protocol: `references/statistical-methods.md`. Compute in code with the user's numbers.

## Output

Pre-registration-style doc: hypothesis, primary metric, unit, MDE + power math (shown), duration, guardrails, analysis plan, stop conditions. Short enough to read; precise enough that analysis is mechanical. After the run → log outcome in the journal; not at target → `ml-iterate`.

## Pipeline integration

Read `ml/PROBLEM.md` for the business metric, cost-of-error, and label maturation facts — don't re-derive them. Save pre-registrations to `ml/experiments/<name>-prereg.md` and append `pre_registered` to `ml/gates.json`. When results close out, the journal entry's expected-vs-actual delta feeds `ml-retro`'s calibration audit — the boomerang only works if the prediction was written down first.
