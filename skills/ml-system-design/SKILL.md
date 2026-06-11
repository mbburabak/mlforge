---
name: ml-system-design
description: >
  This skill should be used when the user asks to "design an ML system", "review this architecture",
  "design a training pipeline", "design a serving architecture", "write an ML design doc",
  "how should we architect" a model/feature/ranking/NLP system, or asks for trade-off analysis
  between ML infrastructure options (batch vs streaming features, real-time vs batch inference,
  embedding stores, model serving on EKS/ECS).
metadata:
  version: "0.2.0"
---

# ML system design

Principal-level ML architecture. Context: AWS, EKS/ECS-centric (not SageMaker), behavioral + NLP problems across transformers, LLMs, classical NLP, user modeling, embeddings, GBMs. Designs must survive a design review, not a survey.

## The iron law

```
NO IMPLEMENTATION WITHOUT A VALIDATED PLAN. AN UNGROUNDED DESIGN IS A GUESS.
```

Verify framework/service claims against docs before putting them in a design. Unverifiable → `[unverified]`. Every number shows its arithmetic.

## Before designing — pin the shaping constraints

Ask only what can't be inferred:

1. **Service contract**: p50/p99 latency, peak QPS, online/batch/async.
2. **Freshness**: how stale before product metrics degrade? This number alone usually decides batch vs streaming.
3. **Data scale + label arrival delay** (behavioral labels arrive hours-to-weeks late — design for it).
4. **Failure tolerance**: model down/wrong → fallback heuristic, cached predictions, or hard dependency?
5. **Ops reality**: who's on call, what infra exists. Undesirable truth: a design the team can't operate is a bad design.

State assumptions explicitly; multiple plausible readings of the ask → present them, don't pick silently.

## Simplicity gate

Before any architecture: what does the simplest thing get? Heuristic → GBM → fine-tune → LLM, in that order of escalation; each rung must beat the previous on the eval, net of added cost. No streaming when batch freshness suffices. No feature store when log-and-wait works. No microservice fan-out when one container serves the QPS. Quantify the gap the complexity buys.

## Design doc shape

1. **Problem & metrics** — business metric, model proxy, and the assumed causal link (state it; it's the most common silent failure).
2. **Constraints** — latency, freshness, cost ceiling, PII.
3. **Architecture** — components, data flow, where state lives. Concrete AWS services.
4. **Alternatives** — ≥2 real options with quantified reasons each loses. "Doesn't scale" without numbers is not a reason.
5. **Failure modes** — per component: what breaks, blast radius, fallback.
6. **Rollout** — shadow → canary → holdback → kill switch.
7. **Cost** — order-of-magnitude with the dominant term flagged, arithmetic shown.
8. **Open questions** — only decision-blocking ones, with owners.
9. **Success criteria** — numeric, measurable, written before build: "p99 < Xms at Y QPS, online metric Z within W% of offline estimate".

## Review mode

Tier every finding: **Blocking** / **Should-fix** / **Consider**. Phrase as failure scenarios ("when the feature pipeline lags, this serves stale scores silently"), not preferences.

Review-killers — check first:

- **Train/serve skew by construction**: feature logic existing twice (offline + online). Blocking. Fix: log-and-wait, shared library, or feature store.
- **Label leakage in pipeline**: feature windows overlapping label windows; joins on future state; aggregates containing the target event.
- **Feedback loops**: model output shaping its own training data (ranking especially). Require logged propensities or exploration traffic.
- **Retrains without gates**: automated retrain → offline gates + canary before promotion. Always.
- **Missing versioning**: every prediction attributable to (model, feature snapshot, code) versions.

## AWS defaults (EKS/ECS)

Details + tables: `references/aws-patterns.md`. Headlines:

- **Serving**: containers on EKS, HPA on queue depth/in-flight (never CPU for GPU work). vLLM/Triton for transformers; FastAPI+ONNX for small models.
- **Training**: Argo Workflows or Step Functions → GPU node groups, Karpenter, spot + checkpointing.
- **Features**: S3+Iceberg offline; DynamoDB/ElastiCache online; Flink-on-Kinesis only when the freshness number demands it, with parity writes to S3 (non-negotiable — that's what kills skew).
- **Retrieval**: OpenSearch k-NN managed; Qdrant on EKS when tuning/cost matters; embedding model version pinned to the index, asserted at query time.

## Behavioral & NLP specifics

- Delayed/censored labels: label maturation policy in the doc — it determines retrain cadence and eval validity.
- User-history features: explicit history cap + cold-start behavior.
- Tokenizer ships with the model artifact, pinned. Tokenizer mismatch = silent quality killer.
- LLM components → route through `llm-engineering`'s decision ladder; don't assume fine-tuning.

## Output

A document pasteable into RFC tooling. Prose, few sections, quantified claims, "(assumption)" on everything unquantified. Diagram only when topology is non-obvious. Dense — no filler.

## Pipeline integration

Read `ml/PROBLEM.md` (constraints, metrics, label reality) and `ml/STACK.md` (infra defaults) before asking the user anything — only ask for what they don't answer. Write the design to `ml/DESIGN.md`. On completed design or review, append `design_reviewed` to `ml/gates.json`. Surface ACTIVE dataset notes from `ml/notes/datasets.md` when the design touches noted data.
