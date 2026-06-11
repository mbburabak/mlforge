---
name: ml-retro
description: >
  This skill should be used for periodic ML engineering retrospectives — when the user says
  "retro", "what did we learn", "review our experiments", "how are we doing", "monthly review",
  or after a milestone/launch. Computes experiment analytics from the journal and distills
  lessons no one computes by hand.
metadata:
  version: "0.3.0"
---

# ML retro

Read the record, compute the truths nobody computes by hand, distill lessons. The journal is data — treat it like data.

## Inputs

`experiments/journal.md`, `experiments/lessons.md`, `ml/gates.json`, `ml/releases/*`, and any boomerang reports. Journal missing or thin → say so; the retro's first lesson is "we don't log enough to learn."

## Compute (in code when the journal is parseable)

1. **Win rate**: experiments where actual ≥ expected, by category (data, HP, architecture, prompt). Typical orgs discover data-category experiments win 2-3× more often than HP sweeps — that finding reallocates the roadmap.
2. **Cost per win**: GPU-hours and wall-time per successful experiment. Trend over time.
3. **Hypothesis calibration**: expected delta vs actual delta across entries. Systematic optimism (predicted +2%, got +0.4%, repeatedly) is the most common bias — quantify it and recommend shrinking future expectations by the observed factor.
4. **Repeat failures**: experiments that retried something the journal already showed failing — count them; each one is process leakage.
5. **Boomerang audit**: for closed pre-registrations and shipped models — predicted MDE vs observed effect, predicted cost vs actual, model-card expected behavior vs canary reality. Plans that consistently miss in one direction get a calibration note.
6. **Hygiene**: unlogged result entries (PLANNED with no outcome), stale `ml/STACK.md` (>90 days), gates being waived repeatedly (a chronically waived gate is either wrong or being dodged — decide which).

## Output — retro report (concise, numbers first)

```markdown
# Retro — [period]
## By the numbers
[win rate by category | GPU-hrs/win | calibration factor | repeat failures]
## What worked / what didn't
[top 3 each, one line, evidence-linked]
## Calibration
[expected-vs-actual bias + concrete adjustment]
## Process leaks
[unlogged runs, dodged gates, retried failures]
## Lessons → distilled
[entries appended to lessons.md this retro]
## Next period bets
[2-3 reallocations the numbers justify]
```

## Distill — the retro's real product

Append patterns to `experiments/lessons.md` (NEVER/ALWAYS rules with dates and sources, per `ml-experiment-journal` format). Then hand candidate rules to `ml-learn` for lifecycle tracking (quarantine → active). A retro that produces no rules was a status meeting.

## Cadence

Weekly during active experimentation, monthly otherwise, always after a launch or incident. Offer to schedule recurring runs if the platform supports it.
