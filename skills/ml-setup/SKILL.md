---
name: ml-setup
description: >
  This skill should be used once per project to capture the ML infrastructure context — when
  the user says "set up mlforge", "configure the plugin", "capture our stack", or when
  another skill notices ml/STACK.md is missing and the user agrees to create it. Interviews
  the user about their stack and writes ml/STACK.md so other skills stop re-asking.
metadata:
  version: "0.3.0"
---

# ML setup

One-time stack interview. Output: `ml/STACK.md` — the file every other skill reads instead of asking "what's your infra" for the fifth time.

## Procedure

1. **Detect before asking.** Scan the repo first: `requirements.txt`/`pyproject.toml`/`Dockerfile`/`k8s` manifests/`.github` reveal frameworks, versions, orchestrators. Pre-fill answers; confirm rather than interrogate.
2. **Interview only the gaps** (use AskUserQuestion when available): compute (GPU types, spot policy, cluster), orchestration (Argo/Step Functions/Airflow), serving (vLLM/Triton/custom, EKS/ECS), feature infra (offline store, online store, streaming), experiment tracking (MLflow/W&B/none), data platform (Spark/Athena/warehouse), label sources and maturation windows, registry/deployment path, cost guardrails (monthly GPU budget, approval thresholds).
3. **Write `ml/STACK.md`**:

```markdown
# Stack
**Updated**: YYYY-MM-DD

## Compute
[GPUs, node groups, spot policy, cluster]

## Orchestration & serving
[orchestrator | serving stack | scaling signals]

## Data & features
[offline store | online store | streaming | data platform]

## Tracking & registry
[experiment tracking | model registry | deployment path]

## Labels
[sources, maturation windows]

## Budgets & guardrails
[GPU budget, cost approval threshold, protected resources (prod tables, registries)]

## Conventions
[seeds, config style, naming, anything the team enforces]
```

4. Append gate `stack_captured` to `ml/gates.json`.

## Rules

- Versions pinned where they matter (torch, transformers, vllm — these change APIs every minor release; other skills verify against the versions recorded here).
- "Protected resources" feeds `ml-careful` — list the tables, S3 prefixes, registries that must never be touched without confirmation.
- Re-run anytime; update in place, bump the date. Stale STACK.md is flagged by `ml-retro` after 90 days.
- Keep it under a page. This is working memory, not documentation.
