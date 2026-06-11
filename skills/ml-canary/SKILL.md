---
name: ml-canary
description: >
  This skill should be used after a model deployment — when the user says "canary", "watch the
  rollout", "monitor the new model", "is the deploy healthy", "post-deploy check", or a
  release produced a CANARY_PLAN.md that now needs executing. Audits production behavior
  against the model card's stated expectations.
metadata:
  version: "0.3.0"
---

# ML canary

Post-deploy watch. The model card made promises; the canary checks them. This is the boomerang — plan vs reality, made explicit and written down.

## Inputs

`ml/releases/<version>/MODEL_CARD.md` ("Expected production behavior" section) and `CANARY_PLAN.md`. No model card → run against best-known expectations, and note that the release skipped `ml-ship` (a process leak for the next retro).

## The checks, per ramp stage

1. **Prediction distribution vs card**: mean/p10/p90 of live scores against the card's stated expectations. Shifted distribution with stable inputs = serving-path suspect → `ml-production-debug` step 3 (don't wait for the online metric to confirm what the score histogram already shows).
2. **Feature health**: per-feature null/default/out-of-range rates vs the card's assumptions. A feature silently going 100% default flattens output with zero errors thrown.
3. **System**: latency p50/p99 vs budget, error rate, throughput at current traffic share.
4. **Flip spot-check**: sample entities scored by both old and new models; flip rate in line with the offline flip analysis? Offline said 8%, live shows 20% → stop the ramp.
5. **Online metric at the pre-registered horizon**: only at the horizon and maturation window the experiment plan committed to. No peeking-driven decisions; sequential bounds if the plan prescribed them.

## Stage gates

Each ramp stage (shadow → N% → 100%) advances only on its CANARY_PLAN numeric gates. A failed gate triggers the rollback plan — which the card already wrote, with numeric triggers and an owner. Execute it; don't renegotiate it mid-incident.

## Output — boomerang report

Append to `ml/releases/<version>/CANARY_REPORT.md` per checkpoint:

```markdown
## Checkpoint [stage, date]
| Check | Card said | Production says | Verdict |
[score dist | nulls | latency | flips | online metric]
**Decision**: advance / hold / rollback — [numeric reason]
```

On completion (100% + horizon passed): final verdict in the report, `canary_passed` (or `rolled_back`) gate appended to `ml/gates.json`, outcome logged in `experiments/journal.md`, and any card-vs-reality miss handed to `ml-retro`'s boomerang audit — systematically wrong cards are a calibration problem, not bad luck.

## Rules

- Checks are computed from real logs/metrics when available — ask for the data, run the comparison in code.
- Drift alerts inform; only guardrail breaches page. Don't convert the canary into alarm fatigue.
- The watch has an end date. A canary that never concludes is monitoring, and belongs to the standing monitors recommended by ml-production-debug.
