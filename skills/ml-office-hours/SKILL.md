---
name: ml-office-hours
description: >
  This skill should be used at the very start of any new ML initiative — when the user says
  "I want to build a model for X", "we need ML for", "new ML project", "should we predict",
  "frame this problem", or describes a product problem they think needs machine learning.
  Runs forcing questions that reframe the problem before any modeling, and writes ml/PROBLEM.md.
metadata:
  version: "0.3.0"
---

# ML office hours

Entry point of the ML sprint: `FRAME → plan → experiment → evaluate → ship → monitor → learn`. Interrogate the problem before anyone touches data. Push back on framing — the stated request is rarely the real problem.

## The iron law

```
NO MODELING WORK UNTIL THE PROBLEM SURVIVES THE FORCING QUESTIONS
```

## The forcing questions — ask, don't skip

Ask conversationally, a few at a time (use AskUserQuestion when available). Demand specifics, not hypotheticals.

1. **Is ML needed at all?** What does the dumb baseline get — a heuristic, a rule, a popularity sort, a lookup table? If nobody can state what the baseline achieves, that's the first deliverable, not a model.
2. **What decision does the prediction drive?** Score → then what? Who/what consumes it, at what threshold, with what action? A score nobody acts on is a dashboard, not an ML system.
3. **What does a wrong prediction cost?** False positive vs false negative, in money or user harm. This sets the metric, the operating point, and how much model quality is even worth.
4. **Do labels exist?** Where, how many, how noisy, and **when do they mature**? (Behavioral labels arrive late — a 30-day conversion window means 30-day-old training data, minimum.) No labels → this is a data collection project first; say so plainly.
5. **What's the causal link between model metric and business metric?** "Better AUC → more revenue" is an assumption. State it explicitly; design how it will be tested (this becomes the experiment plan's primary metric).
6. **What's the freshness and latency reality?** How stale can the score be before the product degrades? Real-time serving is 10× the infra of batch — demand evidence it's needed.

## Reframing duty

After the answers, restate the problem in your own words — and challenge it when warranted: "You said churn model. What you described is intervention targeting — predicting churn is useless unless you also know who's *persuadable*." Extract the capabilities the user described without naming. Offer 2-3 problem framings with effort estimates; recommend the narrowest wedge that ships and teaches something.

## Output — write `ml/PROBLEM.md`

Create the `ml/` directory if absent. Every downstream skill reads this file.

```markdown
# Problem: [name]
**Date**: YYYY-MM-DD  |  **Status**: FRAMED

## Decision this enables
[who acts on the prediction, how]

## Baseline
[the non-ML approach and its (estimated or measured) performance]

## Success metrics
- Business: [metric, target]
- Model proxy: [metric, target]
- Assumed causal link: [stated explicitly] (assumption — tested via experiment)

## Cost of errors
FP: [cost]  |  FN: [cost]  →  operating point implication: [...]

## Labels
Source, volume, noise estimate, maturation window: [...]

## Constraints
Freshness: [...]  |  Latency: [...]  |  Budget: [...]

## Framing decision
Chosen: [wedge]. Rejected: [alternatives + why]. Revisit when: [condition].

## Open questions
[decision-blocking only, with owners]
```

Append to the gate ledger `ml/gates.json`: `{"gate": "problem_framed", "date": ..., "by": "ml-office-hours", "artifact": "ml/PROBLEM.md"}` (create the file with `{"gates": []}` if absent).

## Next

Route forward: infra/architecture questions → `ml-system-design` (reads PROBLEM.md). Stack not yet captured → suggest `ml-setup` once. Ready to plan experiments → `experiment-design`. Or run the whole chain via `ml-autoplan`.
