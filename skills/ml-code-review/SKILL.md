---
name: ml-code-review
description: >
  This skill should be used when the user asks to "review this training code", "review my
  pipeline", "check this model code", "review this PR" for ML code, "is there leakage here",
  "check my data processing", or shares training scripts, feature engineering code, eval
  code, dataloaders, or inference services for review.
metadata:
  version: "0.2.0"
---

# ML code review

ML bugs are distinctive: code runs, metrics look fine, result is wrong. Silent-correctness bugs outrank everything else.

## The iron laws

```
LEAKAGE BEATS ARCHITECTURE — CHECK CORRECTNESS OF THE LEARNING PROBLEM FIRST
REVIEW SURGICALLY — FLAG ONLY WHAT THE DIFF TOUCHES OR BREAKS
NEVER ASSERT A FRAMEWORK BEHAVIOR YOU HAVEN'T VERIFIED FOR THAT VERSION
```

Surgical review: don't demand refactors of untouched code; note unrelated dead code, don't insist on deleting it. Version-specific API claims → verify against installed version/docs or tag `[unverified]`.

## Priority order

1. Correctness of the learning problem (leakage, splits, labels)
2. Eval validity
3. Train/serve parity
4. Reproducibility
5. Performance and cost
6. Style — only when it impedes 1-5

Findings: **Blocking** / **Should-fix** / **Nit**, each with the concrete failing scenario ("user X appears in train and test via…"), not just the rule.

## Leakage & splits — always first

- **Split by the right unit**: rows cluster (events per user, sentences per doc, near-dup texts) → group split. Time-dependent (behavioral ≈ always) → time split, train strictly before test.
- **Temporal leakage**: aggregates computed strictly before each example's timestamp. Watch: current-state dimension joins (future attributes), unbounded window functions, target encoding fit on the full set.
- **Preprocessing leakage**: scalers/vocabs/encoders/imputers/selectors fit on train only — inside the CV loop. `fit_transform` before split = the classic.
- **Label proxies**: features causally downstream of the label. Ask: what's this feature's value at prediction time?
- **Duplicate contamination**: near-dups across splits → group-aware dedup before splitting.

## Eval code

- Right population (silently dropped NaNs shrink denominators; post-prediction filters correlated with correctness).
- Test set untouched by fitting/thresholding/early-stopping — those are validation's.
- Eval decoding/truncation = production intent.
- Ranking: candidate set construction = production retrieval, not oracle.

## NLP traps

- Tokenizer from the same checkpoint/revision; added tokens present both sides; `padding_side` left for decoder-only generation.
- Attention masks passed; loss masked over padding (`ignore_index=-100`); label shift once, not twice (HF causal LMs shift internally).
- Silent truncation: measure % of real inputs over max length, and whether label-relevant content survives.
- BIO realignment at subwords; normalization parity train/inference.

## Training loop & numerics

- Seeds: python/numpy/torch + dataloader workers; "reproducible" ≠ "deterministic" (cudnn) — say which.
- Mixed precision: bf16 preferred; fp16 needs loss scaling; watch custom-loss overflow, `.half()` on layernorms.
- Grad accumulation: loss ÷ accum steps; scheduler per optimizer step, not per batch.
- Checkpoints: optimizer + scheduler + RNG + data position, not just weights.
- Imbalance: weighted loss XOR oversampling, never both; eval on natural distribution.

## Pipelines & services

- Idempotent partitions; explicit dtypes (pandas int→float NaN promotion); tz-aware timestamps (naive datetime in behavioral pipelines = blocking).
- Feature logic duplicated offline/online = should-fix minimum (skew by construction → blocking, see `ml-system-design`).
- Services: model/tokenizer loaded once; `model.eval()` + `no_grad` (prod dropout is real and silent); padding doesn't leak across batched requests; input validation mirrors training preprocessing; backpressure before GPU queues.

Code examples of every pattern: `references/pitfalls.md`.

## Output

Findings by severity: file/line, failing scenario, concrete fix (snippet when short). End with the 2-3 findings that matter most — a review where everything is important is a review where nothing is. Dense; no filler.
