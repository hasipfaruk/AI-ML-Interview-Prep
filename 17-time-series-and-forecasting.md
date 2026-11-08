# 17 — Time Series & Forecasting

Asked in retail, supply chain, finance, energy, ride-sharing, cloud capacity planning, and IoT interviews.

### Contents
1. [Basics](#1-basics)
2. [Stationarity & autocorrelation](#2-stationarity--autocorrelation)
3. [Classical models](#3-classical-models)
4. [Machine learning for time series](#4-machine-learning-for-time-series)
5. [Deep learning & foundation models](#5-deep-learning--foundation-models)
6. [Validation: backtesting](#6-validation-backtesting)
7. [Metrics](#7-metrics)
8. [Probabilistic forecasting](#8-probabilistic-forecasting)
9. [Hierarchical & intermittent demand](#9-hierarchical--intermittent-demand)
10. [Time series anomaly detection](#10-time-series-anomaly-detection)
11. [System design: demand forecasting platform](#11-system-design-demand-forecasting-platform)
12. [What-if scenarios (forecasting)](#12-what-if-scenarios)

---

## 1. Basics

**Q: What makes time series different from normal tabular data?** Observations are ordered and **dependent** on the past. You can't shuffle data randomly, and the future may behave differently from the past.

**Q: Components of a time series?**
- **Trend** — long-term increase/decrease.
- **Seasonality** — repeating pattern with fixed period (daily, weekly, yearly).
- **Cycles** — longer, irregular ups and downs (economic cycles).
- **Noise / residual** — random variation.
Decomposition: additive `y = T + S + R` or multiplicative `y = T × S × R` (when seasonal swings grow with the level). STL is a robust decomposition method.

**Q: Univariate vs multivariate forecasting?** Univariate uses only the series' own history. Multivariate uses other series or covariates (price, promotions, weather, holidays).

**Q: Types of covariates?** **Known future** (calendar, holidays, planned price/promotions), **observed only in the past** (actual weather, competitor sales), **static** (store size, product category). Only known-future covariates can be used directly for future time steps.

**Q: Forecast horizon and granularity?** Horizon = how far ahead (1 day, 12 weeks). Granularity = time step (hourly, daily). Pick based on the decision: staffing needs hourly next-week; factory planning needs weekly next-quarter.

**Q: Point vs probabilistic forecast?** Point = one number. Probabilistic = distribution or quantiles (P10, P50, P90). Business decisions (inventory, capacity) usually need uncertainty.

**Q: Single (local) model vs global model?** Local: one model per series (ARIMA per product). Global: one model trained across many series (LightGBM or deep model over all products) — shares patterns, handles short series better, easier to maintain at scale.

**Q: Recursive vs direct multi-step forecasting?** Recursive: predict t+1, feed it back to predict t+2 (errors compound). Direct: separate model (or output) per horizon. MIMO/seq2seq: predict all horizons at once.

## 2. Stationarity & autocorrelation

**Q: What is stationarity?** Mean, variance, and autocorrelation don't change over time. Many classical models (ARMA) assume it.

**Q: How to test and fix non-stationarity?** Test: plot, rolling mean/std, **ADF** test (null: non-stationary) or **KPSS** (null: stationary). Fix: **differencing** (y_t − y_{t−1}), seasonal differencing (y_t − y_{t−7}), log/Box-Cox transform to stabilize variance, detrending.

**Q: ACF vs PACF?** ACF: correlation of the series with its lags (includes indirect effects). PACF: correlation with a lag after removing effects of shorter lags. Use for ARIMA order: PACF cuts off after p → AR(p); ACF cuts off after q → MA(q).

**Q: What is a random walk and why does it matter?** y_t = y_{t−1} + noise. Best forecast is the last value (**naive forecast**). Many financial series behave like this — always compare models with a naive baseline.

**Q: Baselines you must always try?** Naive (last value), seasonal naive (value same time last week/year), moving average, and drift. If your model doesn't beat seasonal naive, it isn't useful.

## 3. Classical models

**Q: ARIMA(p, d, q)?** AR(p): regression on past values. I(d): differencing d times. MA(q): regression on past forecast errors. **SARIMA** adds seasonal terms (P, D, Q, m). **ARIMAX/SARIMAX** adds external regressors. Select orders with ACF/PACF or auto-ARIMA (AIC).

**Q: Exponential smoothing (ETS)?** Forecast = weighted average of past values with weights decaying exponentially. Simple (level), Holt (level + trend), **Holt-Winters** (level + trend + seasonality). Fast, robust, strong baseline.

**Q: Prophet?** Additive model: trend (with changepoints) + seasonality (Fourier terms) + holidays. Easy for business users, handles missing data and holidays; often beaten by tuned ML models but good quick baseline.

**Q: Limits of classical models?** One model per series (doesn't scale to millions of SKUs easily), limited use of covariates, linear assumptions, struggle with multiple seasonalities and short histories.

**Q: VAR?** Vector autoregression — multiple series that influence each other (e.g., interest rates and inflation).

## 4. Machine learning for time series

**Q: How do you use gradient boosting (LightGBM/XGBoost) for forecasting?** Turn the series into a supervised table:
- **Lag features:** y_{t−1}, y_{t−7}, y_{t−28}
- **Rolling stats:** mean/std/min/max of last 7/28 days (shifted so they only use past data!)
- **Calendar:** day of week, month, holiday flags, days to next holiday, payday
- **Known future covariates:** price, promotion, planned events
- **Static:** store, category (as categorical or target-encoded)
One global model over all series. This won many forecasting competitions (e.g., M5).

**Q: Biggest bug when building lag features?** **Leakage**: rolling windows that include the current or future value, or features computed on the full dataset. Always shift before rolling, and make sure the feature exists at prediction time for each horizon (for horizon 7, lag-1 is not available!).

**Q: How do you handle multiple horizons with tree models?** Direct approach (one model per horizon or horizon as a feature with lags ≥ horizon), or recursive (predict and feed back).

**Q: Target transformations?** Log1p for skewed sales, scaling per series (divide by series mean) so a global model treats big and small series fairly; predict the difference/ratio from a baseline.

## 5. Deep learning & foundation models

| Model | Key idea |
|---|---|
| RNN / LSTM / GRU, DeepAR | sequence models; DeepAR = probabilistic global RNN (Amazon) |
| Temporal CNN (TCN, WaveNet-style) | dilated causal convolutions |
| **N-BEATS / N-HiTS** | pure MLP blocks with backcast/forecast, interpretable trend/seasonal stacks |
| **Temporal Fusion Transformer (TFT)** | handles static, known-future and past covariates; attention + variable selection → interpretable |
| PatchTST, Informer, Autoformer | Transformers for long horizons; patching inputs |
| **Foundation models** (TimesFM, Chronos, Moirai, Lag-Llama) | pretrained on huge collections of series → **zero-shot** forecasting |

**Q: When does deep learning beat gradient boosting?** Many related series, long histories, complex covariate interactions, need for probabilistic multi-horizon output. For small/medium tabular-style problems, LightGBM is often equal or better and much simpler.

**Q: When use foundation models?** Quick baseline, little history, many diverse series, no time to build features. Fine-tune or ensemble with domain models; always backtest — zero-shot doesn't know your promotions.

## 6. Validation: backtesting

**Q: Why not random k-fold?** Future data would leak into training; you'd be "predicting the past from the future" → over-optimistic results.

**Q: How do you validate a forecasting model?** **Rolling-origin backtesting (time-series cross-validation):** train on data up to time T, forecast the next h steps, move T forward, repeat. Expanding window (all history) or sliding window (only recent history).
```
Fold 1: [train..........][test]
Fold 2: [train..............][test]
Fold 3: [train..................][test]
```
Add a **gap** between train and test if features need time to become available (data delays).

**Q: What should the backtest simulate?** Exactly the production setup: the same horizon, the same data availability (data that arrives late in production must be missing in the backtest), the same retraining frequency.

## 7. Metrics

| Metric | Formula idea | Notes |
|---|---|---|
| MAE | mean \|y − ŷ\| | in units, robust, easy to explain |
| RMSE | sqrt(mean (y − ŷ)²) | punishes big errors |
| MAPE | mean \|y − ŷ\| / \|y\| | % — **explodes when y near 0**, biased toward under-forecasting |
| sMAPE | \|y−ŷ\| / ((\|y\|+\|ŷ\|)/2) | symmetric-ish, still unstable near 0 |
| **WAPE** | Σ\|y − ŷ\| / Σ\|y\| | % of total volume — common in retail, stable |
| **MASE** | MAE / MAE of seasonal naive | <1 means better than naive; scale-free, safe near 0 |
| Bias | Σ(ŷ − y) / Σy | systematic over/under-forecasting |
| **Quantile (pinball) loss** | asymmetric loss per quantile | for probabilistic forecasts |
| CRPS | | full distribution quality |
| Coverage | % actuals inside prediction interval | P10–P90 should cover ~80% |

**Q: How to pick a metric?** From the business cost. Over-stock vs stock-out costs differ → forecast a quantile (e.g., P70) and evaluate with pinball loss. Report error weighted by volume or revenue so important items count more.

## 8. Probabilistic forecasting

**Q: How to produce uncertainty?** Quantile regression (LightGBM with quantile objective, one model per quantile), distributional models (DeepAR predicts parameters of a distribution), conformal prediction (calibrated intervals from backtest residuals), bootstrapping residuals, ensembles.

**Q: How do you use a quantile forecast for inventory?** Newsvendor logic: order up to the quantile = cost_understock / (cost_understock + cost_overstock). If stock-outs cost 3× more than leftovers → P75.

**Q: Count data?** Use Poisson/negative-binomial/Tweedie losses (LightGBM `tweedie` objective is popular for retail sales with many zeros).

## 9. Hierarchical & intermittent demand

**Q: What is hierarchical forecasting?** Series form a hierarchy (product → category → total; store → region → country). Forecasts at different levels must add up (**coherence**).
Approaches: bottom-up (sum low-level forecasts — noisy), top-down (split total by proportions — loses detail), middle-out, and **reconciliation** (MinT — optimally combine all levels).

**Q: Intermittent demand (many zeros)?** Spare parts, slow-moving SKUs. Methods: Croston's method (forecast size and interval separately), SBA/TSB variants, Tweedie/zero-inflated models, aggregate to weekly/monthly. Evaluate with MASE/pinball, not MAPE.

**Q: Cold start — new product with no history?** Use similar products (by attributes/embeddings) as analogs, category-level curves, launch plans and price as features, global models with static features; update quickly as real sales arrive.

## 10. Time series anomaly detection

**Q: Approaches?**
- Statistical: z-score on residuals after removing seasonality, rolling median + MAD, control charts.
- Forecast-based: anomaly if actual is outside the prediction interval.
- ML: Isolation Forest on window features, autoencoders/LSTM reconstruction error, matrix profile.
**Q: Common difficulties?** Seasonality causes false alarms (Monday spikes are normal), gradual drifts vs spikes, labels are rare → evaluate with injected anomalies and human feedback, **alert fatigue** → tune thresholds by severity and duration.

## 11. System design: demand forecasting platform
> "Forecast daily demand for 50,000 products × 1,000 stores for the next 8 weeks, to drive replenishment."

**Requirements:** 50M series × 56 days; daily refresh before 6 AM; probabilistic (P50, P90); explain big changes to planners; handle promotions, holidays, new products.

**Design:**
```
Sources: POS sales, inventory (stock-outs!), prices, promo calendar, holidays, weather, product catalog
   → Data lake → daily batch ETL (Spark) → data quality checks (missing stores, late files)
   → Feature pipeline (lags, rolling stats, calendar, promo, price elasticity features)
   → Training (weekly): global LightGBM per category cluster + quantile models
       → backtest gate vs current model and seasonal naive (WAPE, bias, pinball)
   → Inference (daily, batch, distributed): 50M series × horizons
   → Reconciliation (store/region/category totals)
   → Post-processing: business overrides (planner adjustments), caps
   → Forecast store (warehouse table) → replenishment system / planner UI
Monitoring: accuracy by category/store as actuals arrive, bias, drift, missing data alerts
```
**Key deep dives:**
- **Stock-outs censor demand:** sales = 0 because shelf was empty, not because nobody wanted it → mark and impute or exclude those days.
- **Promotions & cannibalization:** promo on one product reduces sales of substitutes.
- **Scale:** batch inference parallelized by store/category; trees are cheap.
- **Human-in-the-loop:** planners override for known events; track whether overrides improve accuracy (they often don't).

---

## 12. What-if scenarios

### The forecast broke after a big shock (COVID-like event, new competitor, a massive holiday shift)
**Causes:** structural break — the past no longer represents the future; models use long history that is now misleading; lag features copy abnormal values forward.
**Isolate:** plot residuals over time; check if error rose for all series at once (global shock) or some segments.
**Fix (now):** shorter training window or heavier weight on recent data, manual planner overrides, switch to faster-adapting models (exponential smoothing), widen prediction intervals.
**Fix (long-term):** add "shock" indicator features, exclude or flag the abnormal period in training later, scenario forecasting, retrain more often.
**Prevent:** monitor rolling error and bias with alerts; have a playbook for regime changes.

### Backtest accuracy is amazing, production accuracy is bad
**Causes (ranked):** **leakage from the future** (rolling features include current day, features computed with full data, using actual promo/price that wasn't known at forecast time, using revised data instead of first-reported data); backtest horizon differs from production; data arrives late in production (yesterday's sales not yet loaded at 6 AM).
**Isolate:** recreate a past forecast exactly "as of" that date with point-in-time data and compare to the backtest output.
**Fix:** point-in-time feature store, shift features, simulate data latency in backtests, gap between train and test.

### New product with no history
See §9 cold start: analog products, attribute-based global model, category curves, launch plan inputs, fast updating with first sales, wider intervals.

### MAPE is huge and unstable
**Cause:** many actual values near zero (low-volume items, intermittent demand) — dividing by tiny numbers.
**Fix:** switch to WAPE, MASE, or weighted metrics; evaluate low-volume items separately; aggregate level for reporting; use pinball loss for decisions.

### Forecast is accurate overall, but bad for specific stores/products
**Causes:** global metric dominated by big series; segment has different behavior (tourist store, new store, local events); missing local features.
**Isolate:** slice errors by store, region, category, volume tier; look at the worst 1%.
**Fix:** segment-specific models or features (store embeddings, local events), cluster series and train per cluster, weight training by business value.

### Forecast is systematically too high (bias)
**Causes:** stock-out days not handled (actually under-forecast then), trend extrapolation, promotions in training not in future, loss function (MSE on skewed data), planners' overrides.
**Fix:** bias metric in monitoring, bias correction, check transformations (log → back-transform needs bias correction), censored demand handling.

### Daily forecast job misses the 6 AM deadline
Upstream data late (add data-arrival SLAs, fall back to yesterday's forecast with flag), job too slow (parallelize by partition, pre-compute features incrementally, smaller models for long tail), monitor job duration trend.

### Planners don't trust the model and override everything
Show explanations (drivers: promo, holiday, trend), forecast-value-added analysis (compare accuracy with and without overrides), involve planners in error reviews, allow structured inputs (events) instead of free overrides.

### Anomaly detector raises too many false alarms
Seasonality not removed, thresholds too tight, alerting on single points. Use seasonal decomposition, require persistence (N points), severity tiers, feedback labels to tune.

### Energy/traffic forecast fails on special days (holidays, sports events)
Add event calendars and "days to/from event" features, similar-day methods (use last year's same holiday), separate model for special days.
