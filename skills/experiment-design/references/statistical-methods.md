# Statistical methods reference

Formulas and procedures for experiment design and analysis. When the user supplies numbers, execute these in Python rather than approximating by hand.

## Power and minimum detectable effect

Two-sample test on means, equal allocation:

```
n_per_arm = 2 * (z_{1-α/2} + z_{1-β})^2 * σ² / δ²
```

- α = 0.05 → z = 1.96; power 0.8 → z = 0.84; the constant 2(1.96+0.84)² ≈ 15.7.
- For proportions, σ² = p(1-p) at the baseline rate.
- MDE given fixed n: `δ = sqrt(2σ²(z_{1-α/2}+z_{1-β})² / n)`.

Relative MDE on a behavioral metric with mean μ: `MDE% = δ/μ`. Behavioral count metrics (sessions, events/user) are heavy-tailed — use the empirical variance from a pre-period, never assume Poisson.

```python
import scipy.stats as st
def mde(n_per_arm, sd, alpha=0.05, power=0.8):
    z = st.norm.ppf(1-alpha/2) + st.norm.ppf(power)
    return z * sd * (2/n_per_arm)**0.5
```

## Ratio metrics (CTR, revenue/session)

When the analysis unit (session, impression) differs from the randomization unit (user), observations are not i.i.d. Use the delta method on per-user sums:

```
Var(X̄/Ȳ) ≈ (1/n μ_y²) [σ_x² - 2(μ_x/μ_y)σ_xy + (μ_x/μ_y)² σ_y²]
```

where X = per-user numerator, Y = per-user denominator. Or bootstrap over users. Computing a naive per-impression variance understates true variance and inflates false positives — this is one of the most common A/B analysis bugs.

## CUPED variance reduction

Adjust the metric with a pre-experiment covariate X (same metric measured pre-period):

```
Y_cuped = Y - θ(X - E[X]),   θ = Cov(X,Y)/Var(X)
```

Variance shrinks by factor (1 - ρ²). Behavioral metrics typically have pre/post correlation ρ ≈ 0.5-0.7 → 25-50% variance reduction → ~25-50% less traffic for the same MDE. New users lack a pre-period; set their covariate to the mean (θ-adjustment is then zero for them).

## Sequential testing (peeking-safe)

- **Group-sequential (O'Brien-Fleming)**: pre-plan k looks; early boundaries are very conservative (first-look z ≈ 4+), final close to 1.96.
- **mSPRT / always-valid p-values**: allows continuous monitoring; pays ~10-30% efficiency vs fixed-horizon. Use when stakeholders will watch dashboards daily.
- Never apply a fixed-horizon t-test repeatedly: 10 peeks at α=0.05 yields ~19% false positive rate.

## Sample ratio mismatch

Chi-square goodness-of-fit on assignment counts vs expected split. p < 0.001 → investigate before reading any metric (bot filtering, redirect asymmetry, logging loss are usual suspects). Even a 50.5/49.5 split on large n is a red flag.

## Paired comparisons for offline eval

For per-example scores from models A and B on the same eval set:

- **Paired bootstrap**: resample examples with replacement B=10,000 times; report CI of the mean difference and P(A>B).
- **Permutation test**: shuffle A/B labels within examples; exact under exchangeability.
- For BLEU/ROUGE-style corpus metrics, bootstrap at the example level and recompute the corpus metric per resample.
- For classification, McNemar's test on the discordant pairs is the classical choice.

```python
import numpy as np
def paired_bootstrap(a, b, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(a) - np.asarray(b)
    boots = rng.choice(d, (B, len(d)), replace=True).mean(axis=1)
    return d.mean(), np.percentile(boots, [2.5, 97.5]), (boots > 0).mean()
```

## Seed variance protocol

For result claims on trained models: ≥3 seeds per arm, report mean ± std, and test arm difference with Welch's t-test over seeds (or report that n_seeds is too small for inference and present the range). If seed std exceeds the claimed improvement, the claim is unsupported — state so.

## Multiple comparisons

- Pre-registered primary metric: no correction.
- Guardrails: non-inferiority tests, each at α=0.05 (they protect, not discover).
- Exploratory scans (many segments × many metrics): Benjamini-Hochberg FDR at 0.05, and label results as exploratory regardless.

## Interference and alternative designs

- **Cluster randomization**: randomize at the level where interference is contained (geo, team, market); analyze with cluster-robust variance. Effective n is the number of clusters, not users.
- **Switchback**: alternate treatment over time units within a unit (for supply/demand systems); account for carryover with burn-in periods and time-block bootstrap.
- **Long-term holdback**: 1-5% of users kept on control for months to measure cumulative/ecosystem effects, especially for ranking systems that shape their own training data.
