# 11 — Statistics, Probability & A/B Testing

Asked in ML engineer, data scientist and applied scientist interviews.

### Contents
1. [Probability](#1-probability)
2. [Distributions](#2-distributions)
3. [Statistics & inference](#3-statistics--inference)
4. [A/B testing](#4-ab-testing)
5. [Classic puzzle questions](#5-classic-puzzle-questions)
6. [What-if scenarios](#6-what-if-scenarios)

---

## 1. Probability

- **Conditional:** P(A|B) = P(A∩B) / P(B).
- **Independence:** P(A∩B) = P(A)·P(B).
- **Bayes' theorem:** P(A|B) = P(B|A)·P(A) / P(B).
- **Expectation** is linear: E[X+Y] = E[X] + E[Y] (always, even if dependent).
- **Variance:** Var(X) = E[X²] − E[X]². Var(aX) = a²Var(X).

**Classic Bayes question:** Disease affects 1% of people. Test is 99% sensitive, 95% specific (5% false positive). You test positive — chance you're sick?
P(sick|+) = (0.99·0.01) / (0.99·0.01 + 0.05·0.99) = 0.0099 / 0.0594 ≈ **16.7%**. Lesson: low base rates → most positives are false (same reason fraud alerts are mostly false).

## 2. Distributions
| Distribution | Use |
|---|---|
| Bernoulli / Binomial | yes/no events, number of successes in n trials (clicks) |
| Poisson | counts per time interval (requests/minute) |
| Normal | sums/averages (Central Limit Theorem) |
| Exponential | time between events |
| Uniform | equal likelihood |
| Power law / long tail | popularity, word frequency |

**Central Limit Theorem:** the mean of many independent samples is approximately normal, whatever the original distribution → why t-tests/z-tests work for averages.

## 3. Statistics & inference

**Q: p-value?** Probability of observing results at least this extreme **if the null hypothesis were true**. It is NOT the probability the null is true.

**Q: Type I vs Type II error?** Type I: false positive (reject a true null), rate = α (usually 0.05). Type II: false negative (miss a real effect), rate = β. **Power** = 1 − β (usually 0.8).

**Q: Confidence interval?** If we repeated the experiment many times, 95% of such intervals would contain the true value.

**Q: Which test?** t-test (compare means), z-test for proportions (conversion rates), chi-square (categorical independence), Mann-Whitney (non-normal), bootstrap (anything, by resampling).

**Q: Correlation vs causation?** Correlation can come from confounders or reverse causation. Causation needs randomized experiments or causal methods (diff-in-diff, instrumental variables, propensity matching).

**Q: Simpson's paradox?** A trend in each group reverses when groups are combined, due to a confounding variable (e.g., different group sizes). Always check segment-level results.

**Q: MLE vs MAP?** MLE maximizes likelihood of data. MAP adds a prior (= regularization: Gaussian prior ↔ L2, Laplace prior ↔ L1).

## 4. A/B testing

**Steps:**
1. Hypothesis + **primary metric** (e.g., conversion) + **guardrail metrics** (latency, revenue, errors).
2. Randomization unit (user, not request — avoid same user seeing both).
3. **Sample size** via power analysis (baseline rate, minimum detectable effect, α, power).
4. Run for full weeks (weekday/weekend cycles); **don't peek** and stop early when significant.
5. Analyze: significance, confidence intervals, segments; check sanity (sample ratio mismatch).
6. Decide considering practical significance, not only statistical.

**Pitfalls to mention:**
- **Peeking** → inflated false positives (use sequential testing if you must).
- **Multiple comparisons** → many metrics/variants → Bonferroni or FDR correction.
- **Novelty / primacy effects** → run longer.
- **Network effects** (social, marketplaces) → cluster randomization.
- **Sample Ratio Mismatch (SRM):** expected 50/50 but got 52/48 → bug in assignment; don't trust results.
- Long-term vs short-term effects → holdout groups.

**For ML models:** offline evaluation → shadow → A/B test. Interleaving for ranking (faster, more sensitive).

## 5. Classic puzzle questions
- **Expected number of coin flips to get heads?** 2 (geometric, 1/p).
- **Birthday problem:** 23 people → >50% chance two share a birthday.
- **Monty Hall:** always switch — 2/3 win chance.
- **Two children, at least one boy — probability both boys?** 1/3.
- **Sample from a stream of unknown length uniformly?** Reservoir sampling: keep the i-th item with probability 1/i.
- **Generate a fair coin from a biased one?** Flip twice: HT → H, TH → T, else repeat.

## 6. What-if scenarios

### A/B test shows +5% conversion, but the effect disappears after launch.
Novelty effect, peeking/false positive, seasonality, SRM bug, segment mix changed. Use holdouts, longer tests, pre-registered analysis.

### Test result is significant for the overall population but negative for mobile users.
Simpson's paradox or genuine heterogeneity. Investigate segments; consider targeted rollout; be careful of multiple-comparison false findings.

### You don't have enough traffic for an A/B test.
Increase MDE, use variance reduction (CUPED — use pre-experiment metric as covariate), run longer, use more sensitive metrics, interleaving, or Bayesian approaches.

### Metric moved, but you suspect it's not from your change.
Check A/A test, seasonality, other concurrent experiments, logging changes, external events.
