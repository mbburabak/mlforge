---
name: tech-leadership
description: >
  This skill should be used when the user asks to "write an RFC", "draft a design doc review",
  "give feedback on this proposal", "help me mentor", "prepare a tech strategy", "write a
  one-pager/two-pager", "make the case for" a technical investment, "push back on" a decision,
  or needs help with principal/staff-level communication: design review feedback, technical
  vision docs, or influencing without authority.
metadata:
  version: "0.2.0"
---

# Technical leadership

Principal/staff-level communication. The bar: every document causes a specific decision or behavior change — name it before writing a word.

## The iron laws

```
NO DOCUMENT WITHOUT NAMING THE DECISION IT EXISTS TO CAUSE
CONCLUSION FIRST, EVERYWHERE
QUANTIFY OR MARK "(ASSUMPTION)"
```

Token economy applies doubly to docs: a 2-pager that gets read beats a 10-pager that gets skimmed. Cut every sentence that doesn't move the decision.

## RFCs / decision docs — default 2-pager

1. **Decision requested** — one sentence, top. Who decides, by when, cost of no-decision.
2. **Context** — minimum for a smart outsider. Link the rest.
3. **Options** — 2-4 real ones incl. "do nothing": cost (build + operate), risk, reversibility, who bears the burden. Strawmen deleted.
4. **Recommendation** — committed, with conditions under which it's wrong ("revisit if traffic > X" beats hedging).
5. **Open questions** — decision-affecting only.

Rules: name disagreements with the dissenter's position stated fairly — a doc that survives the strongest counterargument is the only kind worth sending. ML claims falsifiable: offline→online metric assumptions stated, not implied.

ML-flavored RFCs additionally require: baseline comparison (what does the simple approach get), eval plan before build plan, explicit **kill criterion** — the observed result under which we stop.

## Design review feedback

- Open with what's right — establishes what revisions must preserve.
- **Decision-blocking** vs **advisory**, labeled. The author must know what's required vs ignorable.
- Concerns as failure scenarios: "when the feature pipeline lags, this serves stale scores silently" — not "I'd use streaming".
- Ask the question the design avoids. The best review comment is "what happens when X" for the X the author dodged.
- Calibrate: juniors get the reasoning modeled; peers get the concern and trust.

## Mentoring

- Diagnose before advising: what have they tried, what do they think blocks them. Stated problem ("model not accurate enough") often isn't the real one ("can't push back on the deadline").
- Feedback on observable behavior + impact, not traits. Situation, behavior, effect.
- Toward senior/staff: scope and ambiguity ("own the problem, not the task"), written influence, force-multiplying — their wins become others' wins.
- Don't solve it in the conversation. End with their next action, not yours.

## Influence without authority

- Map the decision-maker's actual currency (risk, cost, timeline, their commitments). Arguments in the wrong currency don't land regardless of merit.
- Concede the opposing view's strongest point first, in writing — buys the credibility the rest spends.
- Propose the experiment, not the conclusion: a reversible trial with a measurement plan is easier to approve than a position.
- Know when to stop: disagree-and-commit explicitly, in writing, with revisit conditions. Relitigating spends standing.

## Output

Match artifact to audience: execs = one page, decision + costs; peers = full options analysis; mixed = one-page summary atop the detail — never one doc straining for both. Prose; tables only for genuine option comparisons.
