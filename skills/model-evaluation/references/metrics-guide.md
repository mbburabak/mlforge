# Metrics guide

Formulas, edge cases, and pitfalls by task family.

## Classification

- **Precision/recall/F1**: report per-class and macro for multi-class with imbalance; micro-averaging hides tail-class collapse. Fβ when the product weighs recall differently (β=2 doubles recall weight).
- **PR-AUC**: preferred under imbalance; note it depends on base rate, so PR-AUC is not comparable across datasets with different prevalence.
- **ROC-AUC**: rank-quality measure, insensitive to calibration and base rate; fine for model comparison on the same data, misleading as a product readiness number under heavy imbalance (0.95 AUC can coexist with useless precision).
- **MCC**: single balanced summary robust to imbalance; good tie-breaker.
- **Threshold selection**: choose on a validation split against the product cost matrix; re-derive after every retrain — score distributions shift even when rank order holds.

## Calibration

- **ECE**: bin predictions (15-20 equal-mass bins beat equal-width), average |accuracy - confidence| weighted by bin mass. Sensitive to binning; report bin count.
- **Reliability diagram** alongside ECE always — ECE can be small while the tails are badly off.
- **Brier score** = calibration + refinement; useful as a single trainable target.
- Fixes: temperature scaling (NNs, single parameter, preserves rank), isotonic regression (flexible, needs ≥~1k samples, can overfit), Platt scaling (logistic, small data). Calibrate on a held-out split, never on the eval set you report.

## Ranking & retrieval

- **NDCG@k**: `DCG@k = Σ (2^rel_i - 1)/log2(i+1)`, normalized by ideal DCG. Use graded relevance when available.
- **Recall@k** for retrieval stages feeding a reranker (did the candidate set contain the answer); **precision@k / MRR** for user-facing results.
- **MAP**: averages precision at each relevant item; stable but opaque to stakeholders.
- Pitfalls: evaluating on the logging policy's exposed items only (position/selection bias — correct with inverse propensity weighting or evaluate on randomized interleaving traffic); pooling judgments from old systems penalizes genuinely novel relevant results.
- **Interleaving** (team-draft) detects ranking preference with ~100x less traffic than A/B on CTR, but measures preference, not long-term outcomes.

## NLP / generation

- **BLEU**: corpus-level n-gram precision with brevity penalty; use sacreBLEU with stated signature or numbers aren't comparable across papers/runs.
- **chrF**: character-level; more robust for morphologically rich languages.
- **ROUGE-1/2/L**: recall-oriented overlap; correlates weakly with summary quality at the system level and barely at the example level — regression guard only.
- **BERTScore / embedding similarity**: catches paraphrase, misses factuality.
- **Factuality/faithfulness**: NLI-based checkers or QA-based (generate questions from source, answer from summary); all imperfect — pair any automated factuality metric with sampled human audit.
- **Perplexity**: comparable only with the same tokenizer and context length; tokenizer changes silently shift perplexity.
- **Span tasks (NER, extraction)**: exact-span F1 plus relaxed-overlap F1; report both, the gap is diagnostic of boundary errors vs detection errors. Use seqeval conventions, beware BIO-tagging off-by-one at subword boundaries.

## Behavioral / user modeling

- **Delayed labels**: evaluate only on matured cohorts (event time + full label window < now). Mixing immature cohorts biases metrics toward fast-reacting users.
- **Censoring**: for time-to-event outcomes use survival metrics (C-index) rather than coercing to binary at an arbitrary cutoff.
- **New vs established users**: always a top-level slice. Models trained on history-rich users routinely fail cold-start; the aggregate hides it because new users are a small share of events but a large share of product growth.
- **Score drift across retrains**: compare score distributions release-over-release (PSI or KS); downstream thresholds and consumers break even when AUC is flat.

## Statistical hygiene

- Bootstrap CIs (over examples; over users when examples cluster within users — clustering inflates effective precision otherwise).
- Paired tests for model comparisons on shared eval sets (see experiment-design skill's statistical-methods reference).
- Multiple slices scanned → BH-FDR correction, and replicate any surprising slice finding on fresh data before acting.
- Minimum slice size: CIs on slices under ~200 examples are usually too wide to act on; merge or collect more before drawing conclusions.

## Eval set construction

- Size by the decision: detecting a 1-point difference at 95% confidence needs roughly thousands of examples for classification, hundreds for paired preference judgments with strong agreement.
- Stratify by the slices you intend to report; oversample tail slices and reweight for aggregates.
- Deduplicate against training data: exact match, then near-dup (MinHash-LSH for text at scale, embedding cosine > ~0.95 spot-check).
- Refresh policy: any eval set older than a few months of product drift is measuring the past; schedule refreshes and keep the old set as a longitudinal anchor.
- Label quality: dual-label a 10% sample, report inter-annotator agreement (Cohen's κ); κ < 0.6 means the task definition, not the model, is the problem.
