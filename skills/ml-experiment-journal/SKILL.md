---
name: ml-experiment-journal
description: >
  This skill should be used when starting, logging, or reviewing ML experiments — when the
  user says "let's try", "run an experiment", "log this result", "what have we tried",
  changes a hyperparameter, swaps a dataset, or modifies a training recipe. Maintains a
  persistent experiment journal with hypotheses, results, and distilled lessons across sessions.
metadata:
  version: "0.2.0"
---

# Experiment journal

Externalize experimental reasoning. Every ML project is a sequence of tested hypotheses — make the sequence visible, persistent, learnable.

## The iron law

```
NO NEW EXPERIMENT WITHOUT LOGGING THE HYPOTHESIS FIRST
```

About to change a hyperparameter, dataset, architecture, prompt, or recipe? Write what you expect and why BEFORE running. "Quick things" get logged too — they compound into knowledge.

## Files

Maintain in project root (create if absent):

```
experiments/
├── journal.md    — append-only experiment log
└── lessons.md    — curated rules (signal, not noise)
```

## Phase 1 — Before any experiment

1. Read `experiments/journal.md` — has this been tried? What happened?
2. Append entry:

```markdown
### YYYY-MM-DD HH:MM — [name]
**Status**: PLANNED
**Hypothesis**: [expected outcome + mechanism]
**Change**: [ONE variable]
**Config**: param: old → new; others unchanged
**Expected**: [specific metric target]
**Baseline**: [current best — written, not remembered]
```

Gate: entry exists before any code runs. No exceptions.

## Phase 2 — After the experiment

Update the entry before starting the next one:

```markdown
**Status**: COMPLETED
**Actual**: [metrics, behavior]
**Delta**: [vs expectation — better/worse/different]
**Duration**: [wall time, GPU hours]
**Learning**: [one sentence]
**Next**: [what this suggests]
```

For statistical claims (this beat baseline): seed variance and paired tests per the `experiment-design` skill before writing "win" in the journal.

## Phase 3 — Before the next iteration

Read journal + lessons. Gate: you can articulate why the next experiment differs from every previous attempt. Need ranked options? → `ml-iterate` skill.

## Phase 4 — Distill (every 3-5 experiments)

A 200-entry journal is noise; lessons are signal. Append to `lessons.md`:

```markdown
## Lessons
- [date] [context]: [lesson]. Source: [experiment / user correction / doc]

## Rules (hard-won)
- NEVER [X] because [reason]. Learned: [date]
- ALWAYS [X] when [condition]. Learned: [date]
```

After any user correction: acknowledge, write the rule that prevents the repeat.

## Anti-patterns

| Mistake | Instead |
|---|---|
| "Just trying this quick thing" unlogged | Log it. 30 seconds now beats re-running it next month |
| Changing LR "while I'm at it" | One variable. Otherwise the result attributes to nothing |
| "I'll remember the baseline" | Write the number. Memory lies |
| "I know what I tried" | Read the journal. You'll find forgotten experiments |
| Journal grows, lessons never distilled | Distill every 3-5 entries |

## Boomerang closing report

When an experiment had a pre-registration (`ml/experiments/<name>-prereg.md`), the Phase 2 entry additionally records plan-vs-reality: predicted effect vs observed, predicted cost vs actual GPU-hours/wall-time, predicted timeline vs reality. These feed `ml-retro`'s hypothesis-calibration stats — the mechanism that detects systematic optimism.

## Behavioral/NLP specifics

- Log label maturation state with every behavioral-metric result — "AUC 0.71 (labels 40% mature)" is a different fact than "AUC 0.71".
- Log tokenizer/template version alongside any fine-tuning config change; it's a variable people forget they changed.
- Online experiment entries: link the pre-registration doc (unit, MDE, duration) from the `experiment-design` skill.
