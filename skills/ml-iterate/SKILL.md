---
name: ml-iterate
description: >
  This skill should be used when the user is stuck or wants ranked next steps after experiments —
  "I tried X and got Y, what next", "metrics plateaued", "model still underperforms", "what
  should we try", or any request for alternatives after an initial training/tuning/retrieval
  attempt didn't hit target.
metadata:
  version: "0.2.0"
---

# Iteration

Ranked, grounded next steps when something was tried and the target wasn't hit.

## The iron laws

```
NO NEW EXPERIMENT WITHOUT REVIEWING WHAT WAS ALREADY TRIED
NO BARE TECHNICAL CLAIMS — EVERY NUMBER GETS A SOURCE OR [unverified]
```

Re-running a failed approach with minor tweaks is the most common waste of GPU time.

## Phase 1 — Review history

1. Read `experiments/journal.md` and `lessons.md` if they exist. Apply ACTIVE rules as constraints; surface relevant QUARANTINE rules as suggestions (see `ml-learn`). Check `ml/notes/datasets.md` for notes on any dataset involved.
2. Restate the user's actual numbers: model, data size, current metric, target, hardware. Every recommendation must reference these — generic advice is not acceptable.
3. Verify understanding of the setup before hypothesizing: model variant (base vs instruct — mismatched variant is Option 0 if found), chat template/tokenizer pairing, label maturity for behavioral metrics.

Gate: you can explain why each proposed option differs from every previous attempt.

## Phase 2 — Diagnose before tuning

Route by symptom, in priority order:

- **Hallucination / wrong entities / factual errors** → data quality FIRST, hyperparameters later. Audit 50-100 training examples for correctness, format consistency, grounding. No LR fixes bad data.
- **Eval worse than baseline after fine-tune** → check loss masking (training on prompt tokens), template mismatch, LR too high (typical LoRA range 1e-5–5e-5 for ≥7B), catastrophic forgetting (probe general capability).
- **Offline good, online bad** → train/serve skew, not a modeling problem → `ml-production-debug` skill.
- **Plateaued metrics** → error analysis before more tuning (`model-evaluation` skill): the failure-mode ranking tells you whether the ceiling is data, label noise, or capacity.
- **Genuinely unclear** → cheapest discriminating test first.

## Phase 3 — Ranked options

Present 2-3 options:

```
### Option N: [name] — expected impact: HIGH/MED/LOW
**What**: [ONE variable change, exact value]
**Why**: [mechanism, tied to their numbers] [source or [unverified]]
**How**: [config/code with # CHANGED: old → new markers + a check that confirms
        the change took effect before the run starts]
**Watch for**: [specific metric, direction, when, mechanism — not "be careful"]
**Effort**: quick / half-day / multi-day
**Risk**: [what could go wrong]
```

Hard rules:

- **One variable per option.** Bundled changes can't be attributed.
- **Proportional change rule**: no parameter moved >3× in one experiment without a cited source justifying the jump. Show the ratio: `1e-4 → 5e-5 (2×)`. Halve or double; never 5× blind.
- **Exact values from their context**, not ranges: "try 2e-5 (down from your 1e-4)", not "try a lower LR".
- **Data/eval options before hyperparameter sweeps** when symptoms point at quality. Data mix, label noise, and loss construction usually dominate LR tweaks.
- Verify any framework kwarg you put in code against docs or the installed version; unverifiable → `# VERIFY`.

## Phase 4 — Recommend one

```
### Next experiment
**Pick**: Option N because [reason]
**Metric**: [name]: current → target
**Checkpoint**: evaluate after [N steps/epochs] — don't wait for the full run
**Success gate**: if [metric ≥ X] proceed; else revert and go to Option M
**Then**: log it in experiments/journal.md (ml-experiment-journal skill) BEFORE running
```

## Anti-patterns

| Mistake | Instead |
|---|---|
| Sweep everything at once | One variable. Attribution beats coverage |
| Only HP options | Data quality, data mix, loss, eval validity usually matter more |
| "Try a lower LR" | "Try 2e-5, half your current 4e-5" |
| 10× parameter jumps | ≤3× per step, show the ratio |
| Success = "looks better" | Numeric gate written before the run |
| Retry past failure with tweaks | Journal says it failed → articulate what's different now |
| Confident version-specific claims from memory | Verify or tag [unverified] |
