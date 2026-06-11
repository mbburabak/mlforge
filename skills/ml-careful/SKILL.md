---
name: ml-careful
description: >
  This skill should be used when the user says "be careful", "guard mode", "freeze",
  "protect prod", before any work touching production data or model registries, or when
  another skill (ml-production-debug) activates it automatically. Adds confirmation gates
  for destructive ML operations and optional edit-scope freezing.
metadata:
  version: "0.3.0"
---

# ML careful

Safety guardrails for ML work. Two modes, composable: **careful** (confirm destructive ops) and **freeze** (lock edit scope). "Guard" = both.

## Careful mode — confirm before destructive operations

Once active (user said "be careful" / "guard", or a skill auto-activated it), require explicit confirmation — restate the operation and its blast radius — before:

- **Data**: `DROP TABLE`/`TRUNCATE`/`DELETE` without `WHERE` on warehouse tables; S3 prefix deletes or overwrites (`aws s3 rm --recursive`, `sync --delete`); overwriting partitions in place; schema migrations on tables feeding features.
- **Artifacts**: deleting checkpoints or experiment directories; force-overwriting a model artifact path; wiping `experiments/` or `ml/`.
- **Registry & prod**: promoting a model version; changing serving config (traffic weights, replicas, model pointer); deleting registry versions.
- **Training data**: changing the retraining data window or filters (silent contamination vector — see ml-production-debug's incident rule).
- **Git**: force-push, `reset --hard`, branch deletion on shared branches.

Resources listed under "Protected resources" in `ml/STACK.md` get this treatment even when careful mode is off.

Confirmation format: what runs, what it destroys, whether it's reversible, then proceed only on explicit yes. User can override any warning — warn, don't block. Never bypass by rewriting the command into an unlisted equivalent.

## Freeze mode — lock edit scope

`freeze <dir>`: all file edits restricted to that directory until unfreeze. Attempted edits outside scope → stop, name the file, ask. Use during debugging so "fixing" doesn't leak into unrelated pipeline code — every unnecessary diff in an ML pipeline is a potential silent regression (see ml-principles, surgical changes).

`ml-production-debug` auto-freezes to the module under investigation once a hypothesis is being tested.

`unfreeze` lifts the boundary. State the freeze scope when activating and on each block.

## Relationship to the guard hook

The plugin's PreToolUse hook (`hooks/scripts/guard.py`) already enforces a deterministic floor on every Bash command — recursive deletes on ML paths, S3 destructive ops, DROP/TRUNCATE, unqualified DELETE, force-push, registry deletion, and training launches without a logged hypothesis — whether or not this skill is active. This skill adds the judgment layer on top: blast-radius explanation, STACK.md protected resources, cost-threshold confirms, freeze scoping, and coverage of operations too context-dependent for regex (partition overwrites, data-window changes, serving config edits).

## Notes

- Reads `ml/STACK.md` for protected resources and cost-approval thresholds (a training launch above the threshold also gets a confirm).
- Modes persist for the session; say so when activating. Deactivate on "stand down" / "normal mode".
- This is friction by design — apply it to destructive ops only, never to reads or analysis. Zero ceremony on safe work.
