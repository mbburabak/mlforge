---
name: ml-autoplan
description: >
  This skill should be used when the user wants a fully reviewed ML plan in one pass — when
  they say "autoplan", "plan this end to end", "run the full planning pipeline", "take this
  from idea to plan", or want framing + design + experiment + eval planning chained
  automatically with only judgment calls surfaced.
metadata:
  version: "0.3.0"
---

# ML autoplan

One command, fully reviewed plan. Chains the planning skills in sprint order with the iron laws encoded as decision principles — surfacing only genuine judgment calls to the user.

## The chain

```
ml-office-hours → ml-system-design → experiment-design → model-evaluation (eval plan)
   PROBLEM.md        DESIGN.md       pre-registration       EVAL_PLAN.md
```

Run each stage's skill in full. Skip a stage only when its artifact already exists and is current (offer to reuse, don't assume).

## Decision principles (auto-applied, not asked)

- Simplicity gate: baseline → GBM → fine-tune → LLM; each rung must justify itself on the eval, net of cost.
- bf16 before QLoRA when VRAM fits; native pipelines before custom; batch before streaming unless the freshness number demands it.
- One variable per experiment arm; seed variance before any claimed win; eval set audited before trusted.
- Every number shows its arithmetic; unverifiable framework claims marked `[unverified]`.

## Surfaced to the user (judgment calls only)

- Primary metric choice when business/proxy trade-offs are real.
- Cost ceiling and latency budget when unstated.
- Problem reframing decisions (ml-office-hours pushback).
- Scope cuts: which slices/segments are launch-blocking vs monitored.

Batch these — one consolidated question round per stage maximum, not a drip.

## Output

A single plan document stitching the four artifacts, plus the gate ledger updated with `problem_framed`, `design_reviewed`, `pre_registered`, `eval_plan` entries. End with the execution strategy: dry-run on 1% → 1 epoch/short run → full run, with a verify step per stage, and the instruction to log the first experiment via `ml-experiment-journal` before any code runs.

## Rules

- This skill orchestrates; it doesn't shortcut. Each stage applies its own full rigor.
- If the user's request is small (one experiment on an existing system), say so and route directly to `experiment-design` — autoplan on a tweak is ceremony, and the principles skill forbids ceremony.
