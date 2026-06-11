---
name: ml-ship
description: >
  This skill should be used when a model is ready to release — when the user says "ship this
  model", "promote to production", "release the model", "is this ready to deploy", "write the
  model card", or asks for a pre-release check. Runs the release readiness dashboard against
  the gate ledger and produces the model card + canary plan.
metadata:
  version: "0.3.0"
---

# ML ship

Model release engineer. A model ships when its gates have run — not when its aggregate metric looks good.

## The iron law

```
NO RELEASE WITH UNWAIVED GATE GAPS — WAIVERS ARE EXPLICIT, NAMED, AND LOGGED
```

## Procedure

### 1. Read the ledger

Read `ml/gates.json`, `ml/PROBLEM.md`, `ml/STACK.md`, and the latest entries in `experiments/journal.md`. Missing ledger → the pipeline wasn't followed; offer to run the missing gates now, in order of cost (cheapest first).

### 2. Release readiness dashboard

Print the dashboard. Required gates by model type — don't demand inapplicable gates (calibration for a rank-only model, golden set for a v1 with no predecessor):

| Gate | Required when | Run by |
|---|---|---|
| `problem_framed` | always | ml-office-hours |
| `design_reviewed` | new system or architecture change | ml-system-design |
| `pre_registered` | a launch experiment will judge it | experiment-design |
| `eval_audit` | always | model-evaluation |
| `seed_variance` | any "better than baseline/predecessor" claim | model-evaluation / experiment-design |
| `slice_analysis` | always | model-evaluation |
| `flip_analysis` + `golden_set` | replacing an existing model | model-evaluation |
| `calibration` | scores consumed numerically or thresholded | model-evaluation |
| `red_team` | leadership-facing claims or high-stakes launch | ml-red-team |
| `rollback_plan` | always | this skill |

Format: `✓ eval_audit (2026-06-10, model-evaluation) · ✗ flip_analysis MISSING · ⚠ seed_variance WAIVED: single-seed LLM fine-tune, cost — accepted by user 2026-06-11`.

### 3. Resolve gaps

For each missing gate: run it now (route to the owning skill), or the user explicitly waives it with a reason — recorded in the ledger as `{"gate": ..., "waived": true, "reason": ..., "date": ...}`. Never silently proceed.

### 4. Produce release artifacts — `ml/releases/<version>/`

**MODEL_CARD.md** (the contract `ml-canary` audits against later):

```markdown
# [model] [version]
**Date** | **Replaces**: [version|none] | **Owner**

## Intended use & consumers
## Training data
[snapshot, date range, known exclusions, label maturation policy]
## Eval results
[headline + CI, slice table, flip summary — link the eval report]
## Expected production behavior        ← canary audits this
[score distribution (mean/p10/p90), latency budget, feature null-rate assumptions]
## Limitations & known failure modes
[from error analysis — honest, specific]
## Versions
[model hash, tokenizer, feature snapshot, code SHA, eval set version]
## Rollback
[trigger conditions (numeric), procedure, owner, decision deadline]
```

**CANARY_PLAN.md**: traffic ramp (shadow → N% → 100%), per-stage success gates (numeric), monitoring checkpoints, the pre-registered online-metric horizon, kill switch.

### 5. Close the loop

Append `shipped` gate with version. Log the release in `experiments/journal.md`. Tell the user the canary watch starts now → `ml-canary`.

## Rules

- Versions are content hashes, not filenames. Tokenizer + preprocessing + model ship as one artifact set.
- Net-improvement releases that break a slice or golden examples are **mitigate-or-waive**, never silent (a +1% aggregate with 8% flips means newly broken users — surface it in the card).
- The rollback plan is written before the release, with numeric triggers. "We'll watch it" is not a plan.
