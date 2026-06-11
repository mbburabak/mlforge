# 🔨 mlforge

> "LLMs are exceptionally good at looping until they meet specific goals... Don't tell it what to do, give it success criteria and watch it go." — Andrej Karpathy

ML engineering has a dirty secret: most of the waste isn't in the models, it's in the process. The wrong problem gets modeled well. Experiments run without a written hypothesis, so nobody can say what was learned. A single-seed "win" becomes a launch decision. A model ships because the aggregate looked good, and three weeks later someone discovers it broke every new user. Production degrades, and the fix is "retrain it" — no diagnosis, no root cause, the same incident scheduled for next quarter.

None of this is a modeling problem. It's a process problem. And process problems are exactly what an agent can enforce.

**mlforge is my answer.** It turns Claude Code into a virtual ML organization — a problem interrogator who pushes back before you model the wrong thing, a statistician who computes power before you launch, an architect who hunts train/serve skew in your design, an evaluator who slices before averaging, a red teamer who breaks your numbers before leadership sees them, a release engineer who refuses to ship past failed gates, an SRE who audits the rollout against the model card's promises, and an eng manager who runs retros on your experiment journal and tells you, with a number, whether your predictions run optimistic.

Nineteen specialists, one heavy-lift agent, two enforcement hooks. All Markdown, all free, MIT license.

**Who this is for:**

- **Principal / staff ML engineers** — who already know the rigor and want it enforced, not remembered
- **ML engineers on AWS** — EKS/ECS serving, Spark pipelines, vLLM, behavioral & NLP workloads
- **Tech leads of ML teams** — release gates, red-team audits, and retros on every model that ships

## Quick start

1. Install mlforge (10 seconds — see below)
2. Say "we need a model for X" — watch it push back on your framing
3. Say "let's try LoRA r=32" — watch it demand a hypothesis first
4. Say "ship it" — watch the readiness dashboard catch your missing flip analysis
5. Stop there. You'll know if this is for you.

## Install — 10 seconds

```
/plugin marketplace add mbburabak/mlforge
/plugin install mlforge@mlforge-tools
```

Zero config. No API keys, no services, no setup wizard. Works in Claude Code and Cowork.

## See it work

```
You:    We need a churn model.
Claude: Pushing back on the framing. Predicting churn is useless unless you
        know who's persuadable — what intervention acts on this score?
        [6 forcing questions: baseline, labels, cost of errors, causal link]
        [writes ml/PROBLEM.md — every downstream skill reads it]

You:    Let's try LoRA r=32 instead of 16.
Claude: Iron law: hypothesis first. Logging to the journal —
        Expected: +1.5% F1 (alpha/r ratio doubles). Baseline: 0.71.

You:    Training finished. Got 0.708.
Claude: Logged. Journal now shows r=64 AND r=32 both failed — your last
        3 hyperparameter changes were all noise-level. Option 1 is data,
        not hyperparameters: audit 100 labels. Your seed std is 0.6%;
        you're tuning inside the noise floor.

You:    Fine. Ship the current model.
Claude: Release readiness:
        ✓ eval_audit   ✓ slice_analysis   ✓ seed_variance
        ✗ flip_analysis MISSING — this replaces ranker-v2.
        Running it... 6.2% of tail users flip correct→wrong.
        Mitigate, or waive with a logged reason?

You:    /mlforge:ml-retro          (three weeks later)
Claude: 14 experiments. Win rate: data changes 4/5, HP changes 1/7.
        Your predicted deltas run 2.8× optimistic. GPU-hours per win
        is trending up. Recommendation: stop sweeping, start auditing.
```

You said "churn model." The agent said "you're building intervention targeting" — because it interrogated the pain, not the feature request. That is not a copilot. That is a team.

## The sprint

mlforge is a process, not a collection of prompts. The skills run in the order an ML project runs:

**FRAME → PLAN → EXPERIMENT → EVALUATE → SHIP → MONITOR → LEARN**

Each skill feeds the next through artifacts. `ml-office-hours` writes the problem doc that `ml-system-design` reads. `experiment-design` writes the pre-registration that `ml-retro` grades against reality. `model-evaluation` appends the gates that `ml-ship` refuses to ship without. Nothing falls through, because every step knows what came before it.

| Skill | Your specialist | What they do |
| --- | --- | --- |
| `ml-office-hours` | **Problem interrogator** | Start here. Six forcing questions before any modeling: is ML needed, what decision does the score drive, what does a wrong prediction cost, do labels exist, what links model metric to business metric. Pushes back on your framing. |
| `ml-autoplan` | **Planning pipeline** | One command: framing → design review → pre-registration → eval plan, iron laws auto-applied. Surfaces only the judgment calls. |
| `ml-system-design` | **Principal architect** | Designs and reviews ML systems with a simplicity gate (heuristic → GBM → fine-tune → LLM) and the review-killers checked first: train/serve skew, leakage paths, feedback loops. AWS/EKS patterns included. |
| `experiment-design` | **Statistician** | Pre-registration rigor: power and MDE arithmetic shown, CUPED, SRM checks, sequential bounds, seed variance, delayed-label handling. Computes with your numbers, in code. |
| `ml-experiment-journal` | **Lab notebook** | No experiment without a logged hypothesis. Append-only journal, distilled lessons, expected-vs-actual on every entry. |
| `ml-iterate` | **Research advisor** | Stuck? Ranked next steps that respect history: one variable per option, ≤3× parameter moves, data-quality options before hyperparameter sweeps, numeric success gates. |
| `model-evaluation` | **Evaluation skeptic** | Audits the eval set before trusting any number. Slices before averaging. Ranks failure modes with counts. Flip analysis and golden sets for replacements; judge controls for LLM evals. |
| `ml-red-team` | **Adversarial reviewer** | Breaks your numbers before leadership sees them: leakage hunt, seed luck, eval contamination, comparison fairness, metric gaming. Attack → evidence → verdict. |
| `ml-ship` | **Release engineer** | The readiness dashboard. Required gates by model type, explicit logged waivers, model card with an expected-behavior contract, rollback plan with numeric triggers — written before launch. |
| `ml-canary` | **SRE** | Audits the rollout against the model card's promises: score distributions, feature health, live flip rate, online metric at the pre-registered horizon. Failed gate → executes the rollback plan, doesn't renegotiate it. |
| `ml-production-debug` | **Incident commander** | Diagnosis before retraining. Timeline → measurement validity → serving path → drift → feedback loops. Three failed fixes → stop and re-plan. |
| `ml-retro` | **Eng manager** | Computes what nobody computes by hand: win rate by experiment category, GPU-hours per win, hypothesis calibration, repeat failures. A retro that produces no rules was a status meeting. |
| `ml-learn` | **Memory** | Lessons graduate quarantine → active → global. Dataset quirks ("events table has dupes pre-2024") auto-surface the next time that table is touched. Gets smarter on your project over time. |
| `llm-engineering` | **LLM lead** | The decision ladder — prompt → RAG → LoRA → full fine-tune — with an eval required before any rung is chosen. Loss-masking gates, vLLM serving, cost levers in order of impact. |
| `ml-code-review` | **Staff engineer** | Finds the bugs that pass CI and still ruin the model: leakage, split hygiene, tokenizer pairing, masking, silent truncation. Bug-pattern library with before/after code. |
| `tech-leadership` | **Staff+ coach** | RFCs that name the decision they exist to cause, with kill criteria. Review feedback split blocking/advisory. Mentoring and influence without authority. |
| `ml-careful` | **Safety officer** | Say "be careful." Confirmation on destructive ops, freeze mode to lock edit scope while debugging. |
| `ml-setup` | **Onboarding** | One-time stack interview → `ml/STACK.md`. Skills stop re-asking about your infra. |
| `ml-principles` | **The constitution** | Iron laws, Karpathy-style coding rules, token economy, stage routing. Loads on any ML task. |

Plus **`ml-expert`** — a heavy-lift agent for framework deep-dives: 8-point hard-gate checklists for training configs (loss masking first) and serving configs (KV-cache math first), every API verified against your pinned versions.

## Hooks: the laws hold even when nobody's looking

Skills advise. Hooks enforce. Two deterministic scripts, zero LLM cost, fail-open by design:

- **Every session starts loaded.** A SessionStart hook injects your project state — problem status, gate ledger, open experiments, active rules — so the agent never starts cold on your repo.
- **Every command is guarded.** A PreToolUse hook stops `DROP TABLE`, S3 recursive deletes, checkpoint wipes, and force-pushes for confirmation — and stops any training launch that has no logged hypothesis in the journal. The iron law is mechanical, not aspirational.

## Plans get graded

Every plan-stage artifact has a reality-stage check. Pre-registrations are graded against journal outcomes. Model cards are graded against canary reports. Predicted costs are graded against actual GPU-hours. `ml-retro` turns the misses into a calibration number — so "we're always optimistic by 3×" becomes a correction, not a personality trait.

## Built on the shoulders of

[Karpathy guidelines](https://github.com/multica-ai/andrej-karpathy-skills) (think before coding, surgical changes) · [caveman](https://github.com/juliusbrussee/caveman) (few token, full substance 🪨) · [gstack](https://github.com/garrytan/gstack) (skills as a pipeline, gates as a ledger, memory that compounds)

## Docs

| Doc | What it covers |
| --- | --- |
| [docs/skills.md](docs/skills.md) | Philosophy and examples for every skill |
| [ARCHITECTURE.md](ARCHITECTURE.md) | The artifact pipeline, gate ledger schema, boomerang pattern |
| [ETHOS.md](ETHOS.md) | The iron laws and why each one exists |
| [CHANGELOG.md](CHANGELOG.md) | What's new in every version |

---

Free, MIT licensed, open source. I built this because the discipline that makes ML teams good is exactly the kind of thing agents can carry for you. Fork it. Improve it. Make it yours.
