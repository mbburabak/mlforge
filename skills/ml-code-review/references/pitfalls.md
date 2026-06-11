# ML bug patterns with examples

Concrete code patterns for the most damaging silent bugs. Use these to recognize variants in review.

## Preprocessing leakage

```python
# BUG: scaler sees test data
X = scaler.fit_transform(df[features])
X_train, X_test = train_test_split(X)

# FIX: fit on train only
X_train, X_test = train_test_split(df[features])
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
```

Same pattern applies to: TF-IDF vocabularies, target encoders, imputers (mean/median), feature selection by correlation with target, PCA. In cross-validation, all fitting goes inside the fold loop — use sklearn `Pipeline` inside `cross_val_score` to make it structural.

## Temporal leakage via joins

```python
# BUG: dimension table holds CURRENT user attributes — future info for past events
events.merge(user_attributes, on="user_id")

# FIX: as-of join against attribute history
pd.merge_asof(events.sort_values("ts"), attr_history.sort_values("valid_from"),
              left_on="ts", right_on="valid_from", by="user_id")
```

Also: rolling aggregates must use windows closed on the left (`.rolling(..., closed='left')` or explicit `< ts` filters); SQL window functions need `ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING`, not the default frame that includes the current row.

## Group leakage in splits

```python
# BUG: same user in train and test
train_test_split(df, test_size=0.2)

# FIX
from sklearn.model_selection import GroupShuffleSplit
tr_idx, te_idx = next(GroupShuffleSplit(test_size=0.2).split(df, groups=df.user_id))
```

Time-based variant: `train = df[df.ts < cutoff]`, and verify feature aggregates in train also respect the cutoff (recomputing features on the full range then splitting rows still leaks).

## HF Transformers traps

```python
# BUG: double label shift — model shifts internally for causal LM
labels = input_ids[:, 1:]           # manual shift
outputs = model(input_ids, labels=labels)  # model shifts again

# FIX: pass labels = input_ids (clone), let the model shift
labels = input_ids.clone()
labels[attention_mask == 0] = -100
```

```python
# BUG: decoder-only generation with right padding — garbage continuations
tok = AutoTokenizer.from_pretrained(name)            # default padding_side="right"
# FIX
tok = AutoTokenizer.from_pretrained(name, padding_side="left")
```

```python
# BUG: resized embeddings not saved with tokenizer
tok.add_tokens(["<user>", "<item>"])
model.resize_token_embeddings(len(tok))
model.save_pretrained(path)   # tokenizer NOT saved → inference loads base tokenizer
# FIX: tok.save_pretrained(path) alongside, load both from `path` at inference
```

Truncation audit: `(df.text.map(lambda t: len(tok(t).input_ids)) > max_len).mean()` — if >2-3% of production-representative inputs truncate, evaluate impact before shipping.

## Loss and masking

```python
# BUG: loss over padding tokens dilutes gradient
loss = F.cross_entropy(logits.view(-1, V), labels.view(-1))
# FIX
loss = F.cross_entropy(logits.view(-1, V), labels.view(-1), ignore_index=-100)
```

BIO alignment after subword tokenization: only the first subword of a word carries the label; continuation subwords get -100. Off-by-one here shows up as suspiciously low span-F1 with high token accuracy.

## Gradient accumulation / scheduler

```python
# BUG: scheduler steps every micro-batch; LR decays accum_steps× too fast
for i, batch in enumerate(loader):
    loss = model(**batch).loss / accum_steps
    loss.backward()
    if (i+1) % accum_steps == 0:
        optimizer.step(); optimizer.zero_grad()
    scheduler.step()          # WRONG PLACE
# FIX: scheduler.step() inside the accumulation if-block, after optimizer.step()
```

## Eval-time mode bugs

```python
# BUG: dropout active during eval/serving
preds = model(x)
# FIX
model.eval()
with torch.no_grad():
    preds = model(x)
```

In services, `model.eval()` belongs at load time; check it's not undone by a stray `model.train()` in shared code paths (e.g., fine-tune endpoint in the same process).

## Pandas silent corruption

- `int` column with NaN → silently `float`; merge keys then mismatch (`1 != 1.0` after astype(str)). Use nullable `Int64` or fill before cast.
- `df.groupby(...).apply(...)` ordering not guaranteed across pandas versions — sort explicitly before positional ops.
- Naive vs aware timestamps: `pd.Timestamp("2026-01-01") < df.ts_utc` raises or, worse, compares wrong after `tz_localize(None)` somewhere upstream. Standardize on UTC-aware at ingestion.
- Chained assignment (`df[df.a>0].b = 1`) silently no-ops; require `.loc`.

## Class imbalance double-correction

```python
# BUG: oversampled data AND weighted loss → tail classes over-corrected
sampler = WeightedRandomSampler(weights, n)
criterion = nn.CrossEntropyLoss(weight=class_weights)
# FIX: pick one; evaluate on the NATURAL distribution either way
```

## Checkpoint/resume

A correct checkpoint saves: model state, optimizer state, scheduler state, scaler state (AMP), epoch/step, RNG states (`torch.get_rng_state`, numpy, python), and dataloader/sampler position (or accept and document that resume reshuffles). Resuming with fresh optimizer state on Adam effectively warm-restarts and can degrade or destabilize — common cause of "resumed run is worse".

## Spark/distributed data

- `rand()` in a column used for splitting recomputes per action → different splits per stage. Materialize the split column (write it out) before use.
- Non-deterministic UDF ordering + `monotonically_increasing_id()` as a join key breaks on retry/recompute.
- Skewed keys (power users in behavioral data) stall joins; salt heavy keys or use AQE skew handling, and check executor-level stragglers before scaling the cluster.
