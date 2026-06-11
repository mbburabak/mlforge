# Roadmap: from skill collection to ML software factory

Inspired by [gstack](https://github.com/garrytan/gstack) — Garry Tan's end-to-end sprint system for Claude Code. gstack's insight is not the individual skills. It's three structural ideas:

1. **Skills form a pipeline, not a toolbox.** Think → Plan → Build → Review → Test → Ship → Reflect. Each skill writes an artifact the next one reads. Nothing falls through because every step knows what came before.
2. **Gates are tracked, not assumed.** `/ship` knows which reviews ran on a branch and refuses (or warns) when one is missing. A readiness dashboard, not a checklist in someone's head.
3. **Memory compounds.** `/learn` persists per-project patterns; taste memory decays and biases future output; lessons graduate quarantine → active → global.

mlforge v0.2 has strong individual skills and a journal. v0.3 turns them into a cycle.

## The ML sprint

```
FRAME → PLAN → EXPERIMENT → EVALUATE → SHIP → MONITOR → LEARN
  │       │         │           │        │       │        │
PROBLEM  DESIGN   journal     EVAL     MODEL   canary  lessons
  .md     .md      .md       REPORT    CARD    log      .md
```

All artifacts live in a `ml/` state directory in the project root (journal/lessons already exist under `experiments/`). Every skill reads upstream artifacts and writes its own. This is the single highest-leverage change: it makes the existing 10 skills compound instead of operating standalone.

## New skills

### Wave 1 — the core loop

| Skill | gstack analog | What it does |
|---|---|---|
| `ml-office-hours` | `/office-hours` | Entry point. Forcing questions before any modeling: is ML needed at all, what does the dumb baseline get, do labels exist and when do they mature, what's the causal link between model metric and business metric, what does a wrong prediction cost, who consumes the score. Pushes back on framing ("you said churn model; you described an intervention-targeting problem"). Writes `ml/PROBLEM.md` that every downstream skill reads. |
| `ml-setup` | `/setup-deploy` | One-time stack interview: orchestrator, serving (vLLM? Triton?), feature infra, tracking, GPU budget, label sources. Writes `ml/STACK.md`. Skills stop re-asking "what's your infra" — they read the file. |
| `ml-ship` | `/ship` | Model release engineer. Reads the gate ledger (below) and runs a **release readiness dashboard**: eval-set audit done? seed variance quantified? slice + flip analysis? golden set passed? calibration checked? rollback plan written? Refuses to produce the model card with unwaived gaps; waivers are explicit and logged. Output: `ml/releases/<version>/MODEL_CARD.md` + canary plan. |
| `ml-retro` | `/retro` | Reads `experiments/journal.md`, computes what no one computes by hand: experiment win rate, GPU-hours per win, hypothesis calibration (expected vs actual delta — are your predictions biased optimistic?), time lost to re-tried failures. Automates lesson distillation (journal Phase 4). Weekly or per-milestone. |

**Gate ledger**: a small `ml/gates.json` each skill appends to (`eval_audit: 2026-06-11, model: v3, by: model-evaluation`). `ml-ship` reads it. This is gstack's "smart review routing" — the CEO doesn't review infra fixes; a calibration gate isn't demanded for a ranking-only model.

### Wave 2 — orchestration and safety

| Skill | gstack analog | What it does |
|---|---|---|
| `ml-autoplan` | `/autoplan` | One command: framing → system design review → experiment pre-registration → eval plan, chained automatically with the iron laws encoded as decision principles. Surfaces only judgment calls (metric choice, cost ceilings) to the user. |
| `ml-careful` | `/careful` + `/freeze` | ML-specific destructive-op guardrails: confirm before `DROP TABLE`, S3 prefix overwrite/delete, checkpoint deletion, experiment-dir wipe, model-registry promotion, retraining-data window changes. `freeze` mode locks edits to one pipeline directory during debugging — `ml-production-debug` auto-freezes to the module under investigation. |
| `ml-canary` | `/canary` | Post-deploy monitoring loop closing the cycle MONITOR stage: prediction-distribution drift vs offline, per-feature null/range, latency, online-metric checkpoint at the pre-registered horizon. Compares against the model card's stated expectations — the **boomerang**: plan vs reality, made explicit. |
| Investigate stop-rule | `/investigate` | Upgrade to `ml-production-debug`: no fixes without a confirmed diagnosis; after 3 failed fix attempts, stop, write up, and re-plan rather than thrash. |

### Wave 3 — compounding intelligence

| Skill | gstack analog | What it does |
|---|---|---|
| `ml-learn` | `/learn` + domain skills | Lesson lifecycle: new rules enter **quarantine**, graduate to **active** after 3 confirmations, optionally **promote to global** (user-level, across projects). Plus dataset domain notes — "events table has dupes before 2024-03", "user_id is reused after deletion" — that auto-fire whenever that table/dataset is touched. The agent gets smarter on *your* data over time. |
| `ml-red-team` | `/codex` second opinion | Adversarial audit of a result before it reaches leadership or a launch decision. Hunts the ways the number could be wrong: leakage, seed luck, eval contamination, SRM, metric gaming, immature labels. Pass/fail gate with concrete break scenarios. Optionally cross-model for true independence. |
| Boomerang reports | plan/live review pairs | Every pre-registration gets a closing report: predicted MDE vs observed effect, predicted cost vs actual GPU-hours, predicted timeline vs reality. Feeds `ml-retro`'s calibration stats. |

## Repo craftsmanship (gstack's other half)

The repo itself is part of the product:

- `ARCHITECTURE.md` — how skills hand off artifacts, the `ml/` state dir contract, the gate ledger schema.
- `ETHOS.md` — the iron laws and where they came from (Karpathy, caveman, gstack).
- `CHANGELOG.md` + `VERSION` discipline — bump on every release, users update via marketplace.
- `docs/skills.md` — deep dive per skill: philosophy, example session, what it writes/reads.
- **CI**: GitHub Action running `claude plugin validate .` + frontmatter lint + a smoke test that every SKILL.md cross-reference points to a real skill.
- **Voice-friendly triggers**: descriptions already trigger on natural phrases ("model dropped", "what next") — audit each skill for spoken-language variants.
- **Proactive stage detection**: ml-principles gains a routing table — notices the user is framing/experimenting/debugging/shipping and suggests the stage skill once, remembers "stop suggesting".

## What we deliberately don't copy

- Browser automation, iOS QA, design pipeline — wrong domain.
- Telemetry, multi-host installers, standalone binaries — premature for a single-plugin repo; revisit if adoption warrants.
- gbrain dependency — the `ml/` file-based state dir gives 80% of the memory value with zero infrastructure, consistent with our no-setup principle.

## Sequencing rationale

Wave 1 first because the artifact pipeline + gate ledger is what converts ten good skills into one system — everything else builds on it. Wave 2 adds the automation and safety that make parallel/long-running work trustworthy. Wave 3 is the compounding layer that pays off over months of use.
