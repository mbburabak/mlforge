# Architecture

How mlforge's skills compose into one system.

## The sprint

```
FRAME → PLAN → EXPERIMENT → EVALUATE → SHIP → MONITOR → LEARN
  │       │         │           │        │       │        │
ml-office ml-system experiment  model-   ml-     ml-      ml-retro
-hours    -design   -design +   evalua-  ship    canary   ml-learn
          llm-eng   journal     tion
```

Cross-cutting: `ml-principles` (rules + stage routing), `ml-iterate` (any stage, when stuck), `ml-production-debug` (incidents), `ml-red-team` (before claims ship), `ml-careful` (safety), `ml-autoplan` (chains FRAME→PLAN), `ml-setup` (one-time), `ml-expert` agent (heavy-lift delegation).

## State directory contract

Skills communicate through files, not session memory. Everything lives in the project root:

```
ml/
├── PROBLEM.md            ml-office-hours → read by everything downstream
├── STACK.md              ml-setup → read instead of re-asking about infra
├── DESIGN.md             ml-system-design
├── gates.json            append-only gate ledger (schema below)
├── experiments/          pre-registrations (experiment-design)
├── evals/                eval reports (model-evaluation)
├── releases/<version>/   MODEL_CARD.md, CANARY_PLAN.md, CANARY_REPORT.md (ml-ship, ml-canary)
└── notes/datasets.md     dataset domain notes (ml-learn)

experiments/              (pre-dates ml/; kept for compatibility)
├── journal.md            append-only experiment log (ml-experiment-journal)
└── lessons.md            rules with lifecycle state (ml-learn)
```

Rules: skills create missing files/dirs on first use; skills read upstream artifacts before asking the user anything; artifacts are markdown (human-owned, git-diffable) except the machine-read ledger.

## Gate ledger — `ml/gates.json`

```json
{
  "gates": [
    {"gate": "problem_framed", "date": "2026-06-11", "by": "ml-office-hours", "artifact": "ml/PROBLEM.md"},
    {"gate": "eval_audit", "date": "2026-06-12", "by": "model-evaluation", "model": "ranker-v3", "artifact": "ml/evals/ranker-v3-2026-06-12.md"},
    {"gate": "seed_variance", "waived": true, "reason": "single-seed LLM fine-tune, cost", "date": "2026-06-13", "by": "ml-ship"}
  ]
}
```

Known gates: `problem_framed`, `stack_captured`, `design_reviewed`, `pre_registered`, `eval_plan`, `eval_audit`, `seed_variance`, `slice_analysis`, `flip_analysis`, `golden_set`, `calibration`, `red_team`, `rollback_plan`, `shipped`, `canary_passed`, `rolled_back`.

Append-only; entries carry `model`/version when model-specific. `ml-ship` is the consumer: it maps model type → required gates and refuses unwaived gaps. Waivers always carry a reason and are surfaced at retro (chronically waived gate = wrong gate or dodged gate).

## The boomerang pattern

Every plan-stage artifact has a reality-stage check:

| Plan | Reality | Compared by |
|---|---|---|
| Pre-registration (expected effect, cost) | Journal closing entry | ml-retro calibration stats |
| Model card (expected prod behavior) | CANARY_REPORT.md | ml-canary, audited by ml-retro |
| Eval plan thresholds | Eval report | ml-ship dashboard |

This is the system's learning loop: plans that consistently miss in one direction become calibration corrections, not repeated surprises.

## Lesson lifecycle

```
QUARANTINE --3 confirmations--> ACTIVE --user--> GLOBAL
     ↑__________contradiction___________|
                    ↓ (2nd contradiction / staleness)
                 RETIRED
```

ACTIVE rules constrain all skills. QUARANTINE rules are suggested, never enforced. Managed by `ml-learn`; fed by retros, corrections, incidents.

## Hooks — the enforcement layer

Skills advise; hooks enforce. Two hooks, both deterministic command scripts (no LLM cost, no added latency worth noticing), both fail-open — a broken guard must never block normal work:

| Event | Script | Does |
|---|---|---|
| `SessionStart` | `session-context.sh` | Loads working memory into every session: PROBLEM status, gate ledger summary, open PLANNED experiments, ACTIVE rules. Silent on non-ML repos. |
| `PreToolUse` (Bash) | `guard.py` | Confirmation gate on destructive ops (recursive deletes on ML paths, S3 deletes, DROP/TRUNCATE, unqualified DELETE, force-push, registry deletion) and on training launches with no PLANNED hypothesis in the journal — two iron laws made mechanical. |

Division of labor: the hook is the always-on floor (regex-detectable, zero judgment); `ml-careful` is the judgment layer (blast radius, protected resources from STACK.md, freeze scoping). The journal-first check is deliberately shallow — it requires *a* PLANNED entry, not the right one; `ml-experiment-journal` owns the semantics. `--dry-run` commands pass freely, consistent with dry-run-first execution.

## Design decisions

- **Files over infrastructure**: the state dir gives most of the memory value of a knowledge base with zero setup, consistent with the no-config install. Revisit only if multi-repo memory becomes a real need.
- **Append-only ledgers** (gates, journal): history is evidence; rewriting it destroys the retro's data.
- **Skills own their gates**: the skill that does the work appends the gate — `ml-ship` verifies, it doesn't re-run.
- **Progressive disclosure**: SKILL.md bodies stay lean; formulas/tables/bug patterns live in `references/`, loaded only when needed.
- **No artificial citation quotas**: grounding discipline (verify-or-tag) without mechanical citation-count requirements.
