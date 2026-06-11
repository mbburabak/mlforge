---
name: ml-learn
description: >
  This skill should be used to manage what the plugin has learned about a project — when the
  user says "remember this", "add a lesson", "what have we learned", "review the rules",
  "note about this dataset", or when a rule from lessons.md is confirmed or contradicted by
  a new result. Manages the lesson lifecycle and dataset domain notes.
metadata:
  version: "0.3.0"
---

# ML learn

Compounding memory. Lessons aren't just appended — they have a lifecycle, so stale or lucky rules don't fossilize into policy.

## Files

```
experiments/lessons.md      — rules with lifecycle state (existing file, extended format)
ml/notes/datasets.md        — per-dataset domain notes
```

## Lesson lifecycle

```
QUARANTINE → ACTIVE (3 confirmations) → GLOBAL (user-promoted)
          ↘ RETIRED (contradicted or stale)
```

Extended `lessons.md` entry format:

```markdown
- [QUARANTINE|ACTIVE|RETIRED] [date] [context]: [rule]. Source: [...]. Confirmations: N. Last-confirmed: [date].
```

- **New rules enter QUARANTINE** — from retros, user corrections, incident postmortems. Quarantined rules are *suggested* in relevant contexts ("a quarantined lesson says X — applies here?"), never silently enforced.
- **Promotion to ACTIVE** after 3 confirmations (a confirmation = a new experiment/incident where the rule held, or explicit user endorsement). Active rules are applied by all skills as NEVER/ALWAYS constraints.
- **Contradiction** → flag immediately, don't quietly keep both. One contradiction sends an ACTIVE rule back to QUARANTINE with the conflicting evidence noted; a second retires it.
- **GLOBAL promotion**: rules the user marks as universal (not project-specific) — offer to copy into the user's global memory (CLAUDE.md or equivalent) since project files don't follow them across repos.
- **Staleness**: rules unconfirmed for 6+ months get flagged at retro for re-validation or retirement.

## Dataset domain notes — `ml/notes/datasets.md`

The ML equivalent of "the Apply button lives in an iframe": facts about *your* data that no documentation records.

```markdown
## events_table
- [ACTIVE, 2026-04] Duplicate rows before 2024-03 (backfill bug) — dedup on (user_id, event_id, ts).
- [QUARANTINE, 2026-06] user_id reused after account deletion — joins across deletion dates suspect.
```

**Auto-fire rule**: whenever work touches a dataset with notes, surface its ACTIVE notes before the first query is written. Same lifecycle as lessons.

## Operations

- **review**: list rules by state, confirmations, staleness. Recommend promotions/retirements.
- **add**: capture a new rule/note into quarantine — one line, dated, sourced.
- **confirm / contradict [rule]**: update count and state; log what moved it.
- **prune**: retire stale rules interactively.
- **export**: emit ACTIVE rules as a block pasteable into CLAUDE.md.

## Rules

- Every rule traces to evidence (journal entry, incident, user correction) — rules without provenance don't get promoted.
- Keep both files lean: ~30 active rules maximum. Beyond that, rules stop being read — distill or retire. Signal, not archive.
- After any user correction in any skill's work: acknowledge, then route the pattern here as a quarantined rule (self-improvement loop).
