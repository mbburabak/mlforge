# Skill deep dives

One section per skill: philosophy, trigger, what it reads/writes. Sprint order.

## FRAME

### ml-office-hours
The most expensive ML mistake is solving the wrong problem well. Six forcing questions (is ML needed, what decision does the score drive, cost of errors, label reality, metric→business causal link, freshness) plus a duty to push back on framing. **Reads**: nothing. **Writes**: `ml/PROBLEM.md`, gate `problem_framed`. **Say**: "we need a model for X", "frame this problem".

### ml-setup
Infrastructure context captured once instead of re-asked forever. Detects from the repo before interviewing. **Writes**: `ml/STACK.md` (including protected resources for `ml-careful`), gate `stack_captured`. **Say**: "set up mlforge", "capture our stack".

## PLAN

### ml-system-design
Principal-level architecture with a simplicity gate (heuristic → GBM → fine-tune → LLM) and review-killers checked first: train/serve skew by construction, leakage paths, feedback loops, ungated retrains. AWS/EKS reference library included. **Reads**: PROBLEM.md, STACK.md. **Writes**: `ml/DESIGN.md`, gate `design_reviewed`. **Say**: "design this system", "review this architecture".

### llm-engineering
The decision ladder — prompt → RAG → LoRA → full fine-tune — with an eval required before any rung is chosen. Loss-masking and tokenizer gates, vLLM serving and cost levers. **Say**: "fine-tune or prompt?", "design a RAG system".

### experiment-design
Pre-registration-grade rigor: power/MDE arithmetic, CUPED, SRM, seed variance, delayed labels. Statistical methods reference with runnable code. **Reads**: PROBLEM.md. **Writes**: `ml/experiments/<name>-prereg.md`, gate `pre_registered`. **Say**: "design this A/B test", "how big a sample".

### ml-autoplan
The planning chain in one command, iron laws auto-applied, only judgment calls surfaced. Routes small asks directly to `experiment-design` instead of ceremonializing them. **Say**: "autoplan", "plan this end to end".

## EXPERIMENT

### ml-experiment-journal
Hypothesis written before the run, result logged before the next run, lessons distilled every 3-5 entries. The journal is the retro's dataset. **Writes**: `experiments/journal.md`, `experiments/lessons.md`. **Say**: "let's try", "log this result".

### ml-iterate
Ranked next steps that respect history: one variable per option, ≤3× parameter moves, data-quality options before HP sweeps, numeric success gates with failure plans. **Reads**: journal, lessons, dataset notes. **Say**: "I tried X and got Y, what next", "metrics plateaued".

## EVALUATE

### model-evaluation
Audit the eval set before trusting any number; slice before averaging; rank failure modes with counts. Flip analysis and golden sets for model replacements; judge controls for LLM evals. **Writes**: `ml/evals/`, gates `eval_audit`/`slice_analysis`/`flip_analysis`/`golden_set`/`calibration`/`seed_variance`. **Say**: "evaluate this model", "error analysis".

### ml-red-team
Adversarial audit before a number reaches leadership: leakage hunt, seed luck, eval validity, comparison fairness, metric gaming, story-data consistency. Attack → evidence → verdict. **Writes**: gate `red_team`. **Say**: "red team this", "is this number real".

## SHIP

### ml-ship
The release readiness dashboard: required gates by model type, explicit logged waivers, model card with expected-production-behavior contract, canary plan with numeric stage gates, rollback plan written before launch. **Reads**: gates.json + everything. **Writes**: `ml/releases/<version>/`, gate `shipped`. **Say**: "ship this model", "is this ready to deploy".

## MONITOR

### ml-canary
Audits production against the model card's promises: score distributions, feature health, latency, live flip rate, online metric at the pre-registered horizon only. Failed gate → execute the rollback plan, don't renegotiate it. **Writes**: `CANARY_REPORT.md`, gate `canary_passed`/`rolled_back`. **Say**: "watch the rollout", "is the deploy healthy".

### ml-production-debug
Incident runbook in probability order: timeline → measurement validity → serving path → drift → feedback loops. Three-strikes stop rule; auto-freezes scope; never lets a retrain eat incident-window data. **Say**: "model performance dropped", "predictions look wrong".

## LEARN

### ml-retro
Computes what nobody computes by hand: experiment win rate by category, GPU-hours per win, hypothesis calibration (are your predictions systematically optimistic?), repeat failures, boomerang misses. A retro that produces no rules was a status meeting. **Say**: "retro", "what did we learn".

### ml-learn
Lesson lifecycle (quarantine → 3 confirmations → active → optional global) and dataset domain notes that auto-fire when noted data is touched. Thirty active rules max — signal, not archive. **Writes**: `experiments/lessons.md`, `ml/notes/datasets.md`. **Say**: "remember this", "review the rules".

## CROSS-CUTTING

### ml-principles
The operating system: iron laws, think-before-coding, simplicity first, surgical changes, goal-driven execution, grounding, token economy, and the stage-routing table. Loads on any ML build/fix/train/deploy ask.

### ml-code-review
Silent-correctness review — code that runs, metrics that look fine, results that are wrong. Leakage and split hygiene first; NLP traps (tokenizer pairing, masking, truncation); bug-pattern library with before/after code. **Say**: "review this training code", "is there leakage here".

### tech-leadership
RFCs that name the decision they exist to cause, with kill criteria; review feedback split blocking/advisory; mentoring and influence without authority. **Say**: "write an RFC", "help me push back".

### ml-careful
Confirmation on destructive ops (DROP, S3 deletes, checkpoint wipes, registry promotion), freeze for edit-scope locking. Friction on destructive operations only. **Say**: "be careful", "guard", "freeze".

### ml-expert (agent)
Heavy-lift delegation: training-config reviews (8-point hard gate, loss masking first), serving reviews (8-point, KV-cache math first), framework deep-dives with version-verified APIs. Use for multi-step framework work where one silent misconfig wastes a training run.
