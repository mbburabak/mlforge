---
name: llm-engineering
description: >
  This skill should be used when the user asks "should we fine-tune or prompt", "design a RAG
  system", "fine-tune this model", "build an LLM feature", "reduce LLM costs", "evaluate our
  LLM pipeline", "set up vLLM", "LoRA vs full fine-tuning", or needs guidance on LLM system
  architecture, fine-tuning strategy, prompt management, or LLM serving and cost optimization.
metadata:
  version: "0.2.0"
---

# LLM engineering

Simplest approach that meets the quality bar wins — and the bar is an eval, defined before any approach is chosen. "We'll fine-tune" before "here's our eval set" = the project failing in advance.

## The iron laws

```
EVAL BEFORE BUILD — NO APPROACH CHOSEN WITHOUT THE EVAL THAT JUDGES IT
EXHAUST EACH RUNG OF THE LADDER BEFORE CLIMBING
NEVER GUESS A FRAMEWORK KWARG — VERIFY AGAINST THE PINNED VERSION OR MARK # VERIFY
```

Plans must be grounded: verify API signatures and config keys against docs for the pinned version (transformers/peft/trl/vllm change every minor release). Pin with `==`. Every VRAM/throughput/cost number shows its arithmetic.

## The decision ladder

1. **Prompting a strong hosted model** — few-shot from real data, structured outputs. Hours to iterate. The baseline every rung must beat on the eval, net of cost.
2. **RAG** — when the failure is missing/stale/private knowledge. Doesn't fix reasoning, style, or format failures — diagnose the failure type first.
3. **Fine-tuning (LoRA/QLoRA first)** — consistent style/format/domain behavior that in-context examples can't pin; or distillation for latency/cost; or static instructions dominating prompt length. Needs hundreds-to-thousands of quality examples.
4. **Full fine-tune / continued pretraining** — adapters demonstrably underfit (rare; demand LoRA evidence first).

Document the rung chosen and the eval delta that justified passing each cheaper one.

## Eval first

- 150-300 examples from real traffic + real failures, crisp pass criteria, before model selection.
- Per-failure-mode breakdown: "fails multi-hop" is actionable; "82% good" isn't.
- Judge validated against human labels (`model-evaluation` skill).
- **Prompt changes are deploys**: full eval re-run on every change. Log experiments via `ml-experiment-journal`; plateaus → `ml-iterate`.

## RAG

- **Retrieval first**: most RAG failures are retrieval failures. Measure retriever recall@k on labeled (query → gold passage) pairs before touching prompts.
- Earning-their-keep defaults: hybrid BM25+embedding fusion; structure-aware chunking with overlap; metadata filters before vector search; cross-encoder reranker when k must be small.
- **Embedding version pinned to the index, asserted at query time.** Reindex strategy decided before the first index.
- Groundedness: citations required; faithfulness evaluated (claims ⊆ retrieved); measure the unanswerable case — a RAG that never says "not in the docs" hallucinates by design.
- Freshness: incremental indexing + tombstones; stale docs masquerade as model failures in triage.

## Fine-tuning

- LoRA defaults: r=16-64 swept, alpha=2r (state the alpha/r ratio — it matters more than absolute rank), all linear layers, LR 1e-4–2e-4 cosine, 1-3 epochs. Overfitting small SFT sets is fast: watch repetitive generation + benchmark regression.
- **Loss masking is mandatory**: completion-only loss for instruction tuning; training on prompt tokens is the #1 silent killer. pad = eos for decoder-only (never unk); tokenizer + template saved with the adapter.
- **Data is the work**: dedupe, decontaminate vs eval set, personally audit 100 random examples. Filter hard; scale doesn't average out bad data.
- **Forgetting check**: general-capability probes alongside task eval; task-perfect + instruction-following-broken fails in composition.
- Distillation: strong model generates on real input distribution → quality-filter → train small → compare at matched latency/cost. State quality-per-dollar.
- bf16+LoRA before QLoRA when VRAM fits: `params × 2 bytes + optimizer + activations ≤ 0.85 × VRAM`. Show the math.
- DPO etc. only after SFT plateaus, with genuinely contrastive pairs. Most product cases never need it.
- Deliverable includes the merge/export script and an inference smoke test on the merged model. Adapter without merge = half-shipped.

## Serving & cost (EKS/vLLM)

- vLLM, continuous batching; scale on queue depth/in-flight tokens. Separate interactive and batch deployments of the same model.
- Cost levers in order: exact-match cache → router to smaller/distilled model for easy traffic → quantization (AWQ/int8, eval re-run after) → prompt compression → hardware tuning.
- Structured outputs: constrained decoding (schema/grammar), not "please output JSON" — kills the parser-retry failure class.
- Tokens in/out per request per route, alerted on drift: a template change doubling input tokens shows up in the bill, not in errors.

## Prompt management

Prompts in version control, code-level review bar; golden-input renders diffed in CI; model versions pinned and eval re-run on every provider bump (treat as dependency upgrade); (prompt version, model version, params) logged with every production response.

## Output

"Should we X" → recommendation with the ladder applied to their case, eval plan, cost arithmetic, kill criterion. Build requests → design or code with the eval harness included; runnable, pinned, no stubs.
