# Ethos

## The iron laws

```
NO MODELING WORK UNTIL THE PROBLEM SURVIVES THE FORCING QUESTIONS
NO IMPLEMENTATION WITHOUT A VALIDATED PLAN
NO EXPERIMENT WITHOUT LOGGING THE HYPOTHESIS FIRST
NO NEW EXPERIMENT WITHOUT REVIEWING WHAT WAS ALREADY TRIED
ONE VARIABLE PER EXPERIMENT
NO TRUSTED NUMBER FROM AN UNAUDITED EVAL SET
NO BARE TECHNICAL CLAIMS — GROUND IT OR TAG IT [unverified]
NO FIX WITHOUT A CONFIRMED DIAGNOSIS
NO RELEASE WITH UNWAIVED GATE GAPS
ASSUME THE NUMBER IS WRONG — THE AUDIT FINDS HOW
```

Iron laws are cheap to follow and expensive to violate. Each one exists because its violation has a known, recurring, costly failure mode: GPU-hours burned on unattributable experiments, launches judged on leaked metrics, incidents extended by symptom-fixes, leadership decisions made on seed luck.

## Provenance

This plugin steals deliberately, from three sources:

- **[Karpathy-inspired guidelines](https://github.com/multica-ai/andrej-karpathy-skills)** — think before coding, simplicity first, surgical changes, goal-driven execution. The four LLM failure modes (wrong assumptions, overcomplication, orthogonal edits, weak success criteria) are exactly the failure modes of ML work itself.
- **[caveman](https://github.com/juliusbrussee/caveman)** — token economy. Few tokens, full substance. Dense skill files load faster and steer better; dense answers get read. Brain big, mouth small.
- **[gstack](https://github.com/garrytan/gstack)** — the system shape: skills as a pipeline connected by artifacts, gates tracked in a ledger rather than assumed, plan/reality boomerangs, memory with a lifecycle, safety guardrails on demand, and a repo that documents its own architecture.

## Beliefs

**ML failures are usually data failures.** The runbooks check the data path before the model, every time. "Retrain it" without a diagnosis is a cost center.

**The aggregate is hiding something.** Slices, flips, and failure modes drive decisions; single numbers decorate dashboards.

**Plans are predictions, and predictions are gradeable.** Write the expectation down before the run; compare after; correct the calibration. A team that never grades its predictions stays optimistic forever.

**Simplicity is a gate, not a vibe.** Heuristic → GBM → fine-tune → LLM. Each rung must beat the previous on the eval, net of cost, or you don't climb.

**Memory must be curated to compound.** An append-only journal is data; thirty active rules are policy; three hundred unreviewed rules are noise. Quarantine, confirm, promote, retire.

**Friction belongs on destructive operations only.** Confirmation gates on `DROP TABLE` and registry pushes; zero ceremony on reads, analysis, and trivial fixes. Judgment over ritual — rigor is for the work that can waste a week.
