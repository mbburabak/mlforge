# Changelog

## 0.4.0 — 2026-06-11

The enforcement release: skills advise, hooks enforce.

- **Renamed**: `principal-ml` → **`mlforge`** (plugin), `principal-ml-tools` → **`mlforge-tools`**
  (marketplace). Install: `/plugin install mlforge@mlforge-tools`.

- **SessionStart hook** (`session-context.sh`): loads project working memory into every
  session — PROBLEM status, gate ledger summary, open PLANNED experiments, ACTIVE rules.
  Silent on non-ML repos.
- **PreToolUse guard** (`guard.py`): deterministic confirmation gate on every Bash command —
  destructive ops (recursive deletes on ML paths, S3 deletes, DROP/TRUNCATE, unqualified
  DELETE, force-push without lease, registry deletion) and training launches with no PLANNED
  hypothesis in the journal. Two iron laws made mechanical. Fail-open by design; `--dry-run`
  passes freely.
- `ml-careful` documents its division of labor with the guard (hook = deterministic floor,
  skill = judgment layer); ARCHITECTURE.md hooks section; validator now checks hooks.json
  and script existence; guard covered by an 11-case test.

## 0.3.0 — 2026-06-11

The gstack release: from skill collection to end-to-end ML sprint cycle.

**New skills (9):**
- `ml-office-hours` — forcing-question problem framing; writes `ml/PROBLEM.md`
- `ml-setup` — one-time stack interview; writes `ml/STACK.md`
- `ml-ship` — release readiness dashboard against the gate ledger; model card + canary plan
- `ml-retro` — journal analytics: win rate by category, GPU-hours/win, hypothesis calibration
- `ml-autoplan` — chains framing → design → experiment → eval planning, surfaces only judgment calls
- `ml-careful` — destructive-op confirmation gates + edit-scope freeze
- `ml-canary` — post-deploy watch auditing production against the model card (boomerang)
- `ml-learn` — lesson lifecycle (quarantine → active → global) + dataset domain notes
- `ml-red-team` — adversarial result audits before claims reach leadership

**System:**
- `ml/` state directory contract — skills communicate through artifacts (ARCHITECTURE.md)
- Gate ledger (`ml/gates.json`) — gates tracked, not assumed; explicit logged waivers
- Boomerang pattern — pre-registrations, model cards, and canary reports graded against reality
- Stage routing table in `ml-principles`; pipeline-integration blocks in all v0.2 skills
- `ml-production-debug`: three-strikes stop rule + auto-freeze
- Repo: ARCHITECTURE.md, ETHOS.md, docs/skills.md, docs/ROADMAP.md, CI validation

## 0.2.0 — 2026-06-11

Principles alignment (Karpathy guidelines, caveman):
- New: `ml-principles`, `ml-experiment-journal`, `ml-iterate` skills; `ml-expert` agent
- Iron laws + grounding gates across all skills; token-economy rewrite
- Marketplace packaging (`.claude-plugin/marketplace.json`), MIT license

## 0.1.0 — 2026-06-11

Initial release: 7 skills (system design, experiment design, model evaluation, production
debug, code review, tech leadership, LLM engineering) with reference libraries (AWS/EKS
patterns, statistical methods, metrics guide, ML bug patterns).
