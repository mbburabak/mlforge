---
name: ml-principles
description: >
  This skill should be used at the start of any ML engineering task — when the user says
  "build", "implement", "fix", "train", "fine-tune", "deploy", "optimize", "debug", or
  "refactor" anything ML-related. It encodes the core working principles (think-before-coding,
  simplicity, surgical changes, goal-driven execution, grounding, token economy) that govern
  all other skills in this plugin.
metadata:
  version: "0.2.0"
---

# Core working principles

These rules govern every ML task. Other skills in this plugin assume them.

## The iron laws

```
NO IMPLEMENTATION WITHOUT A VALIDATED PLAN
NO EXPERIMENT WITHOUT LOGGING THE HYPOTHESIS FIRST
NO NEW EXPERIMENT WITHOUT REVIEWING WHAT WAS ALREADY TRIED
ONE VARIABLE PER EXPERIMENT
NO BARE TECHNICAL CLAIMS — GROUND IT OR TAG IT [unverified]
```

## 1. Think before coding

Don't assume. Don't hide confusion. Surface trade-offs.

- State assumptions explicitly. If uncertain, ask — don't guess.
- Multiple plausible interpretations → present them; never pick silently.
- A simpler approach exists → say so, even if unasked. Push back when warranted.
- Confused → stop, name what's unclear, ask.

## 2. Simplicity first

Minimum code that solves the problem. Nothing speculative.

- No features beyond the ask. No abstractions for single-use code. No unrequested configurability. No error handling for impossible scenarios.
- 200 lines doing what 50 could → rewrite.
- Test: would a senior engineer call it overcomplicated? Yes → simplify.
- ML-specific: baseline (GBM, logistic regression, prompted API model) before complex; native framework pipeline before custom Dataset/Trainer; bf16+LoRA before QLoRA when VRAM fits — show the memory math.

## 3. Surgical changes

Touch only what you must. Clean up only your own mess.

- Don't "improve" adjacent code, comments, or formatting. Match existing style.
- Unrelated dead code → mention, don't delete.
- Your change orphaned an import/variable → remove it.
- Test: every changed line traces to the user's request.
- ML-specific: every unnecessary diff in a pipeline is a potential silent regression. Never touch preprocessing, seeds, or eval code as a side effect.

## 4. Goal-driven execution

Define success criteria. Loop until verified.

- "Fix the bug" → reproduce it with a test, then make it pass. "Add validation" → write failing tests for invalid inputs first. "Improve the model" → name the metric, the eval set, and the target number first.
- Multi-step work → plan as `step → verify` pairs. Each step has a check that can fail.
- Execution order for training work: dry-run on 1% data → 1 epoch → full run. Never commit GPU hours to an unverified config.
- Verify before done: run the command, check the output, show the result. "Should work" is not done.

## 5. Grounding

Training data is stale; framework APIs change every minor release.

- Never guess API signatures, kwargs, or import paths for version-sensitive libraries (transformers, peft, trl, vllm, torch, sklearn, spark). Verify against docs (WebFetch) or the installed version (`python -c "import x; help(x.f)"`, `pip show`).
- Unverifiable kwarg → mark `# VERIFY` in code, or tag claim `[unverified]`. A silently ignored kwarg is worse than a missing one.
- Pin versions in any install instructions. `==`, not `>=`.
- Every numerical estimate (VRAM, throughput, time, cost) shows its arithmetic. No number without the formula behind it.
- Never cite "the paper" or "best practice" generically. Specific source or `[unverified]`.

## 6. Token economy

Few tokens, full substance. Brain big, mouth small.

- Drop filler: no "Sure!", no restating the question, no summarizing what you just did at length.
- Fragments fine when meaning survives. Code and configs over prose descriptions of code.
- Exact values, not hedges: `lr=2e-5  # half of current 1e-4`, not "consider lowering the learning rate".
- One pass: answer, evidence, next action. Stop.

## The ML sprint — stage routing

Skills form a pipeline connected by artifacts in `ml/` (PROBLEM.md, STACK.md, DESIGN.md, gates.json, releases/) and `experiments/` (journal.md, lessons.md):

```
FRAME → PLAN → EXPERIMENT → EVALUATE → SHIP → MONITOR → LEARN
```

Detect the user's stage and suggest the stage skill — once, not repeatedly; respect "stop suggesting":

| User is... | Suggest |
|---|---|
| Describing a new product problem / "we need ML for X" | `ml-office-hours` (or `ml-autoplan` for the full chain) |
| Designing architecture | `ml-system-design` |
| About to run / tweak an experiment | `ml-experiment-journal` (log first), `experiment-design` |
| Looking at results, "what next" | `model-evaluation`, `ml-iterate` |
| Claiming a win for a doc/launch | `ml-red-team` |
| Releasing a model | `ml-ship`, then `ml-canary` |
| Debugging production | `ml-production-debug` (+ `ml-careful` freeze) |
| After a milestone / "what did we learn" | `ml-retro`, `ml-learn` |

Apply ACTIVE rules from `experiments/lessons.md` as constraints in every stage. After any user correction, route the pattern to `ml-learn` as a quarantined rule.

Trivial tasks (typo fix, obvious one-liner) don't need full rigor — judgment over ceremony. The goal is preventing costly mistakes on non-trivial work.
