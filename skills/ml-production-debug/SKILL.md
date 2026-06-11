---
name: ml-production-debug
description: >
  This skill should be used when the user reports "model performance dropped", "predictions look
  wrong in production", "metrics regressed after deploy", "data drift", "feature drift", "the
  model works offline but not online", "scores shifted", or needs to triage a production ML
  incident, investigate training/serving skew, or diagnose a data quality issue.
metadata:
  version: "0.2.0"
---

# Production ML debugging

ML failures are usually data failures. Rule out causes in probability order; don't jump to retraining.

## The iron laws

```
DIAGNOSIS BEFORE REMEDIATION — "RETRAIN" WITHOUT A ROOT CAUSE TREATS THE SYMPTOM
ONE HYPOTHESIS AT A TIME, CHEAPEST DISCRIMINATING TEST FIRST
NO FIX WITHOUT A CONFIRMED DIAGNOSIS — STOP AFTER 3 FAILED FIXES AND RE-PLAN
```

Drive the triage: state the leading hypothesis + its probability + the cheapest test that confirms or kills it. Given logs/data → analyze in code directly.

**Scope freeze**: once a hypothesis is under test, activate `ml-careful` freeze on the module under investigation — debugging must not leak "improvements" into unrelated pipeline code.

**Three-strikes rule**: three fixes attempted without resolution → stop. Write up what was tried, what each attempt ruled out, and the surviving hypotheses. Re-plan from the evidence (or escalate) rather than thrash — a fourth blind fix is how incidents acquire second incidents.

## Runbook — in order, each step halves the search space

### 1. Timeline (5 min)

When did it move? Correlate: model deploys, feature pipeline changes, upstream schema changes, retrains, product/UI changes shifting traffic mix, marketing, calendar. **Sharp step → something shipped. Slow bleed → drift or feedback.**

### 2. Verify the measurement

- Metric definition / logging / join logic changed?
- Label lag: "regression" = immature labels in recent cohorts?
- Mix shift: compute within fixed segments. Per-segment flat + aggregate moved = Simpson's, not model failure. Different fix.

### 3. Serving path (most common true cause)

- **Feature skew**: served feature vectors (from prediction logs) vs offline recompute, same entities/timestamps. Top offenders: null-handling, timezone/window boundaries, stale online store, silent default fallbacks.
- **Null/default rates over time per feature**: a feature going 100% default flattens output, throws no errors.
- **Version mismatch**: model + preprocessing + tokenizer/vocab in prod match the trained pair. NLP: tokenizer drift = plausible-looking, degraded predictions. Check hashes, not filenames.

### 4. Only then, drift

- **Covariate**: PSI/KS per feature, training snapshot vs recent serving. Rank by importance × PSI, not PSI alone; PSI > 0.2 on important features = actionable.
- **Prediction drift**: score distributions release-over-release. Shifted scores + stable inputs → pipeline/model change; shifted inputs → upstream.
- **Concept drift**: inputs stable, input→label relation changed. Detect: frozen model on freshly matured labels. The only category where retraining is the actual fix.
- **Embedding/text drift**: distance-to-training-centroids; new topics and language mix evade token stats.

### 5. Feedback loop (ranking/behavioral)

Model shapes its own training data → slow self-inflicted decay: popularity reinforcement, exploration collapse. Check: exploration/propensity logging alive? Holdback cohort same trend? Holdback degraded equally → external cause; only treated → the loop.

## Stabilize, then fix

Mitigations fastest-first: rollback model, pin/repair feature with sane default, route segment to fallback, **freeze automated retrains**. Never let a retrain consume incident-window data uncleaned — converts an outage into persistent contamination.

## Post-incident

Recommend the cheapest monitor that catches this class earliest: per-feature null/range at serving > prediction distribution per version > sampled offline/online parity > label-joined online metric > drift dashboards. Page only on must-act-within-hours. Log the incident + lesson into `experiments/lessons.md` (`ml-experiment-journal`): the NEVER/ALWAYS rule that prevents the repeat.
