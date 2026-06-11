---
name: ml-red-team
description: >
  This skill should be used before an ML result reaches leadership or a launch decision —
  when the user says "red team this", "challenge this result", "is this number real",
  "sanity check before I present", "audit this claim", or ml-ship requires the red_team
  gate for a high-stakes release. Adversarially audits how the number could be wrong.
metadata:
  version: "0.3.0"
---

# ML red team

Adversarial audit of a result. The job is not to validate — it's to break the claim, and report whether it survived. A number that hasn't been attacked isn't evidence yet.

## The iron law

```
ASSUME THE NUMBER IS WRONG — THE AUDIT'S JOB IS TO FIND HOW
```

## The attack list — run all that apply

1. **Leakage hunt**: split unit (rows cluster by user/doc/time?), temporal joins, preprocessing fit on full data, label proxies in features, near-duplicate contamination across splits, eval set decontamination vs training data. Cheapest test for each (per ml-code-review's checklist).
2. **Seed luck**: how many seeds? Single-seed improvement under ~2× the known seed std = unproven. How many configurations were tried before this one — and is this the best of N reported as if it were the only run (garden of forking paths)?
3. **Eval validity**: who built the eval set, when, label error rate, distribution match to production now (not at collection time). Did the threshold/decoding settings come from the same set being reported?
4. **Comparison fairness**: equal tuning budget for the baseline? Same eval examples, same preprocessing, same candidate sets (ranking)? Paired test or aggregate eyeballing?
5. **Online-result attacks**: SRM, peeking without sequential bounds, immature labels, mix shift masquerading as effect (segment-level check), pre-registered metric or post-hoc selected winner among many metrics scanned?
6. **Metric gaming**: does the proxy improve while plausibly degrading the actual goal (CTR up via clickbait, recall up via threshold shift, ROUGE up via extraction)? What second metric would expose it — and was it measured?
7. **Story-data consistency**: do the numbers in the doc match the numbers in the artifacts? Same model version, eval set version, date ranges? Claims like "all configs" or "every segment" backed by actual coverage?

## Procedure

Read the claim and its artifacts (eval report, journal entries, experiment plan, gate ledger). Run the applicable attacks — compute on the actual data/predictions when available, don't eyeball. For each: **attack → evidence → verdict** (broken / weakened / held).

## Output

```markdown
# Red team: [claim]
**Verdict**: SURVIVED / SURVIVED WITH CAVEATS / BROKEN

| # | Attack | Result | Evidence |
[only attacks that ran; one line each]

## Required corrections
[what must change in the claim/doc before presenting — exact wording]
## Residual risk
[what couldn't be tested and what it could hide]
```

Append `red_team` gate to `ml/gates.json` with the verdict. BROKEN → the claim doesn't ship to leadership until corrected; route findings back to the owning skill (`model-evaluation`, `experiment-design`).

## Rules

- Independence: audit from the artifacts, not from the author's narrative. When genuinely independent review matters (the author is this same assistant in the same session), recommend a fresh session or a second model for the audit, and say why.
- Tone: attack claims, never people. The deliverable protects the presenter — a leadership doc that survives red team won't ambush them in the meeting.
- Don't manufacture doubt: a clean result gets a clean verdict, fast. Rubber-stamp suspicion is as useless as rubber-stamp approval.
