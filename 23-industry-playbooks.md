# 23. Industry Playbooks: AI/ML Interviews in Every Industry

Interviewers at a bank, a hospital or a game studio ask the same ML questions, but they expect answers that fit **their** world:
their regulations, their cost of mistakes, their data. This chapter gives you that context for 20 industries.

For each industry you get:
1. **Use cases:** the top AI/ML problems.
2. **Data & constraints:** data types, regulation, latency, cost of errors, explainability.
3. **Business metrics:** what the company actually cares about.
4. **Case study:** one compact system design.
5. **What-ifs:** industry-specific scenario questions with model answers.
6. **Vocabulary:** terms the interviewer expects you to know.

### Contents
0. [How to adapt any answer to any industry](#0-how-to-adapt-any-answer-to-any-industry)
1. [Healthcare & life sciences](#1-healthcare--life-sciences)
2. [Banking, finance, insurance & fintech](#2-banking-finance-insurance--fintech)
3. [E-commerce & retail](#3-e-commerce--retail)
4. [Advertising & marketing tech](#4-advertising--marketing-tech)
5. [Social media & content platforms](#5-social-media--content-platforms)
6. [Search engines](#6-search-engines)
7. [Autonomous vehicles & robotics](#7-autonomous-vehicles--robotics)
8. [Manufacturing & IoT](#8-manufacturing--iot)
9. [Telecom](#9-telecom)
10. [Logistics, supply chain & delivery](#10-logistics-supply-chain--delivery)
11. [Energy & utilities](#11-energy--utilities)
12. [Education (edtech)](#12-education-edtech)
13. [HR tech & recruiting](#13-hr-tech--recruiting)
14. [Legal & compliance](#14-legal--compliance)
15. [Cybersecurity](#15-cybersecurity)
16. [Gaming](#16-gaming)
17. [Travel & hospitality](#17-travel--hospitality)
18. [Media, entertainment & streaming](#18-media-entertainment--streaming)
19. [Agriculture](#19-agriculture)
20. [Government & public sector](#20-government--public-sector)
21. [Which chapters to study for each industry](#21-which-chapters-to-study-for-each-industry)

---

## 0. How to adapt any answer to any industry

Before you answer any design or "what if" question for a specific company, run this checklist in your head.
If you say 2-3 of these points out loud, the interviewer can tell you understand their business.

| Question to ask yourself | Why it changes the design | Example |
|---|---|---|
| **Who is harmed by an error, and how badly?** | Decides precision vs recall, thresholds, human review | Missed cancer (very bad) vs a bad movie recommendation (minor) |
| **Which regulations apply?** | Decides data storage, explainability, audit logs, consent | HIPAA (health), GDPR (EU data), fair lending laws, EU AI Act |
| **What is the latency budget?** | Decides batch vs real-time, model size | Fraud check < 100 ms; crop yield forecast: daily batch is fine |
| **Where do labels come from?** | Decides how fast you can train and evaluate | Clicks (instant), chargebacks (30-90 days), doctors (expensive) |
| **How delayed is feedback?** | Decides monitoring strategy | Loan default after months → use proxy metrics |
| **Does the decision need to be explained?** | Decides model choice (simple vs deep), SHAP, reason codes | Loan denial must give reasons by law |
| **How sensitive is the data?** | Decides privacy tech: anonymization, on-prem, federated learning | Patient records, children's data, location |
| **Is there an adversary?** | Decides robustness, fast retraining, monitoring | Fraudsters, spammers, hackers, cheaters adapt to your model |
| **What is the cost of being down?** | Decides fallback strategy: fail-open vs fail-closed | Payments fail-open with rules; medical device fail-safe |
| **Is there a fairness risk?** | Decides slice evaluation, bias audits | Hiring, lending, policing, healthcare |
| **Edge or cloud?** | Decides model compression, offline operation | Cars, factory cameras, farms with weak internet |

**One sentence that works in every industry interview:**
> "Before choosing a model, I'd like to understand the cost of each type of error here, the regulations we must follow, and how quickly we get feedback labels, because those three decide most of the design."

---

## 1. Healthcare & life sciences

**Use cases:** medical imaging diagnosis (X-ray, CT, MRI, pathology), clinical note summarization and coding (ICD codes), patient risk prediction (readmission, sepsis), drug discovery (molecule property prediction, protein structure), clinical trial matching, medical chatbots and triage, hospital operations (bed and staff forecasting), wearable signal analysis (ECG, glucose).

**Data & constraints:**
| Aspect | Details |
|---|---|
| Data | images (DICOM), EHR tables, clinical text, genomics, time-series vitals |
| Regulation | HIPAA (US), GDPR, FDA / CE approval for medical devices (Software as a Medical Device), audit trails |
| Cost of errors | very high: missed diagnosis harms patients; false alarms cause alarm fatigue |
| Explainability | doctors must understand and trust outputs; the AI supports, the doctor decides |
| Labels | expensive (specialist time), noisy (doctors disagree), small datasets |
| Privacy | de-identification, on-prem or private cloud, federated learning across hospitals |

**Business metrics:** sensitivity/specificity at clinically chosen operating point, time saved per clinician, reduction in readmissions, diagnostic turnaround time, regulatory approval, clinician adoption rate.

**Case study: sepsis early warning in a hospital**
- Requirements: alert nurses 4-6 hours before sepsis, using vitals and lab results every 15 minutes; low false-alarm rate; explanation for each alert.
```
Bedside monitors + lab system + EHR (HL7/FHIR feeds)
        │
        ▼
Streaming ingestion (Kafka) → feature builder (rolling vitals, lab trends, missingness flags)
        │
        ▼
Risk model (gradient boosting / time-series model) → calibrated risk score + top contributing factors (SHAP)
        │
        ▼
Alert policy (threshold + suppression: no repeated alerts within 4h) → nurse dashboard / pager
        │
        ▼
Clinician feedback (acted / dismissed) + outcomes → monitoring & retraining (with clinical review board)
```
- Deep dives: **alarm fatigue** (precision matters a lot; tune threshold with clinicians), **missing data is informative** (a lab test being ordered is a signal), patient-level train/test split, temporal validation (train on 2022, test on 2023), validation at new hospitals before rollout (site shift), **silent mode** pilot before alerts go live.

**What-ifs:**
- **Model trained at Hospital A performs poorly at Hospital B.** Causes: different devices, patient population, coding practices, lab units. Isolate: compare feature distributions and per-site metrics. Fix: local fine-tuning or recalibration, multi-site training, federated learning. Prevent: external validation for every new site before go-live.
- **Doctors ignore the alerts.** Too many false alarms, no explanation, alerts at the wrong time or in the wrong tool. Fix: raise threshold, add reasons, integrate into existing workflow, co-design with clinicians; measure "alerts acted on".
- **Imaging model detects the hospital's scanner, not the disease** (shortcut learning). Use saliency maps (Grad-CAM), test on other scanners, remove text markers, balance data across sites.
- **A patient asks the medical chatbot about chest pain.** Safety first: detect emergencies and route to "call emergency services now"; never diagnose; ground answers in vetted medical sources; human escalation; log and review.
- **Radiologists disagree on 20% of labels.** Use consensus labels (majority or adjudication), model the uncertainty, measure inter-rater agreement (Cohen's kappa) as the performance ceiling.

**Vocabulary:** EHR/EMR, FHIR, HL7, DICOM, HIPAA, PHI (protected health information), de-identification, SaMD, FDA 510(k), sensitivity/specificity, PPV/NPV, AUROC, calibration, alarm fatigue, clinical validation, prospective vs retrospective study, ICD codes.

---

## 2. Banking, finance, insurance & fintech

**Use cases:** fraud detection (cards, payments, account takeover), credit scoring and loan underwriting, anti-money laundering (AML), algorithmic trading and price forecasting, insurance claims triage and pricing, customer churn, KYC document verification, chatbots for banking, financial document extraction.

**Data & constraints:**
| Aspect | Details |
|---|---|
| Data | transactions (high volume, tabular), credit bureau data, documents, market time series |
| Regulation | fair lending laws (ECOA, FCRA in US), model risk management (SR 11-7), Basel, PCI-DSS (card data), GDPR, explainability for adverse actions |
| Latency | fraud: < 100 ms at authorization; credit: seconds to minutes; trading: microseconds to milliseconds |
| Cost of errors | missed fraud = money lost; false decline = angry customer, lost revenue |
| Explainability | required: "reason codes" for loan denials; models are validated by a separate model risk team |
| Adversary | yes: fraudsters adapt quickly |

**Business metrics:** fraud loss (basis points of volume), false positive rate / decline rate, approval rate at fixed default rate, expected loss, customer lifetime value, AML alerts reviewed per analyst and true-positive rate (SAR conversion).

**Case study: credit scoring for instant loans**
- Requirements: decision in < 5 s, explain denials with top reasons, fair across protected groups, auditable.
```
Application → KYC/identity check → feature assembly (bureau data, income, bank transactions via open banking)
           → Rules (hard policy: age, sanctions list) → Scoring model (GBDT, monotonic constraints)
           → Calibrated probability of default → decision policy (approve / reject / manual review, limit & price)
           → Reason codes (SHAP top features mapped to approved text) → audit log (inputs, model version, decision)
Outcomes (repayment months later) → performance monitoring → annual model validation & retraining
```
- Deep dives: **reject inference** (you never see outcomes for rejected applicants → biased training data), monotonic constraints (more income should never increase risk), fairness testing (disparate impact ratio), champion/challenger, model documentation for regulators.

**What-ifs:**
- **Fraud model's false declines doubled after a holiday sale.** Distribution shift: more first-time buyers, bigger baskets, new merchants. Mitigate: temporary threshold adjust and step-up authentication (OTP) instead of hard declines. Long-term: seasonal features, faster retraining, segment-level thresholds.
- **Regulator asks why a customer was denied.** Show reason codes, input data, model version, and the validation report; that is why you log everything and use explainable models or SHAP-based explanations.
- **Model approves fewer women than men at equal risk.** Measure approval and default rates by group; check proxy features (zip code, shopping categories); remove or constrain proxies; fairness-aware thresholds with legal review; document.
- **Fraud ring uses many new accounts that look normal one by one.** Add graph features (shared devices, IPs, addresses), graph ML or link analysis, velocity features across accounts.
- **Trading model was profitable in backtest, loses money live.** Look-ahead bias, survivorship bias, overfitting to history, ignoring transaction costs and slippage, regime change. Fix: walk-forward validation, realistic cost modeling, paper trading before live.

**Vocabulary:** PD/LGD/EAD (probability of default, loss given default, exposure at default), KS statistic, Gini coefficient, reason codes, adverse action notice, model risk management, AML, KYC, SAR, chargeback, step-up authentication, open banking, backtesting, look-ahead bias, basis points.

---

## 3. E-commerce & retail

**Use cases:** product recommendations, search ranking, dynamic pricing, demand forecasting and inventory, customer segmentation, churn and lifetime value, product categorization and attribute extraction, review summarization, visual search, AI shopping assistants, return prediction, fake review detection.

**Data & constraints:** clickstream (huge, implicit feedback), product catalog (text + images), transactions, inventory. Latency: search and recs < 200 ms. Cost of errors: lost sales (medium). Seasonality is strong (holidays, sales events). Cold start for new products is constant.

**Business metrics:** conversion rate, GMV (gross merchandise value), revenue per visitor, average order value, add-to-cart rate, search exit rate / zero-result rate, forecast accuracy (MAPE, WAPE), stock-out rate, inventory holding cost, return rate.

**Case study: demand forecasting for 50,000 products × 1,000 stores**
```
Sales history + promotions + prices + holidays + weather + store info
        │
        ▼
Feature pipeline (lags, rolling means, promo flags, price elasticity, calendar)
        │
        ▼
Global model (LightGBM or deep forecasting model across all series) + hierarchy reconciliation (store → region → total)
        │
        ▼
Probabilistic forecasts (P10 / P50 / P90) → replenishment optimizer (order quantity vs holding & stock-out cost)
        │
        ▼
Store orders → actual sales → accuracy monitoring by category
```
- Deep dives: one global model vs per-series models, intermittent demand (many zeros), **censored demand** (sales = 0 because out of stock, not because no demand), new products (use similar-product features), forecast quantiles because the business decision depends on uncertainty.

**What-ifs:**
- **Recommendation clicks went up but revenue went down.** Recs push cheap or discounted items; optimize a revenue-aware or multi-objective score; add guardrail metrics.
- **Forecast badly missed during a promotion.** Promo not in features, or new promo type; cannibalization of other products. Add promo features, uplift models, planner overrides with feedback.
- **Search returns zero results for 15% of queries.** Spelling errors, synonyms, other languages, out-of-catalog items. Fix: spell correction, synonym mining from query logs, semantic search, query relaxation; track zero-result rate.
- **Dynamic pricing raised prices during an emergency and caused bad press.** Add business rules and price caps, human approval for large changes, fairness and reputation checks; not everything should be optimized.
- **Fake reviews are rising.** Classifier on text + behavior (account age, review bursts, purchase verified), graph of reviewer-seller links, human moderation for top sellers.

**Vocabulary:** GMV, AOV, conversion funnel, CTR, add-to-cart, basket analysis, collaborative filtering, cold start, price elasticity, cannibalization, SKU, stock-out, safety stock, MAPE/WAPE, hierarchical forecasting, uplift modeling.

---

## 4. Advertising & marketing tech

**Use cases:** click-through rate (CTR) and conversion rate (CVR) prediction, real-time bidding, budget pacing, audience targeting and lookalike modeling, attribution, creative generation and testing, customer lifetime value, marketing mix modeling, uplift modeling for campaigns.

**Data & constraints:** billions of impressions per day, extremely sparse categorical features, delayed conversions (hours to days). Latency: bid decisions in ~10-100 ms. Privacy: cookie deprecation, consent (GDPR, CCPA), Apple ATT. Calibration matters because predicted probabilities directly set bid prices.

**Business metrics:** revenue, ROAS (return on ad spend), CPA (cost per acquisition), CPM/CPC, advertiser retention, auction efficiency, calibration error, incremental lift.

**Case study: CTR prediction for an ad platform**
```
Ad request (user, context, page) → candidate ads (targeting filters, budget available)
   → feature lookup (user embeddings, ad history, context) → CTR & CVR models (deep + cross / wide & deep, embeddings for sparse IDs)
   → expected value = bid × pCTR × pCVR (+ quality score) → auction (second-price / first-price) → ad served
Impression / click / conversion logs → joined with delay handling → online/continuous training → calibration check
```
- Deep dives: **calibration** (bids depend on exact probability), **delayed feedback** (a non-click now may convert later), feature hashing for huge ID spaces, continuous training because ads change daily, exploration for new ads.

**What-ifs:**
- **Predicted CTR is accurate on average but advertisers overpay.** Calibration drift per segment; recalibrate (isotonic per segment), monitor predicted/actual ratio per campaign.
- **Third-party cookies disappear.** Shift to first-party data, contextual targeting (page content embeddings), privacy-preserving APIs, aggregated measurement, modeled conversions.
- **Campaign shows high conversions but finance says no real sales increase.** Attribution counts people who would have bought anyway; measure **incrementality** with holdout groups or geo experiments; uplift modeling.
- **A new ad never gets shown (cold start).** Exploration budget (bandits), priors from similar ads/advertiser, content features of the creative.
- **Click fraud from bots.** Bot detection (behavior patterns, IP/device reputation), filter invalid traffic before billing and training.

**Vocabulary:** CTR, CVR, CPM, CPC, CPA, ROAS, RTB, DSP/SSP, second-price vs first-price auction, bid shading, pacing, calibration, attribution (last-click, multi-touch), incrementality, uplift, lookalike audiences, MMM, invalid traffic.

---

## 5. Social media & content platforms

**Use cases:** feed ranking, friend/follow suggestions, content moderation, spam and fake account detection, notification ranking, trending topics, creator recommendations, ad integration, misinformation detection, AI-generated content labeling.

**Data & constraints:** user graph, posts (text, images, video), engagement events at massive scale. Latency: feed < 200 ms. Integrity and safety are critical; regulation (EU Digital Services Act), elections, child safety laws. Adversaries: spammers, bot networks, coordinated campaigns.

**Business metrics:** DAU/MAU, time spent, sessions per user, retention, meaningful interactions, creator retention, reports per 1k views, prevalence of violating content, appeal overturn rate.

**Case study: fake account detection**
```
Signup / activity events → real-time rules (rate limits, known bad IPs) → block obvious bots
                         → feature store (device fingerprint, signup velocity, behavior sequences, graph features)
                         → models: account-level classifier + graph model (clusters of linked accounts)
                         → actions by confidence: allow / challenge (CAPTCHA, phone verify) / restrict / remove
                         → appeals + human review → labels → retraining (weekly or faster)
```
- Deep dives: adversarial adaptation (attackers probe your thresholds), graph-based cluster takedowns, false positives on real users (appeals), measuring **prevalence** with random sampling rather than only counting removals.

**What-ifs:**
- **Engagement-optimized feed is spreading outrage content.** Proxy metric problem; add integrity signals, downrank borderline content, optimize for long-term satisfaction surveys and retention, not raw engagement.
- **Moderation model removes posts in one language much more often.** Bias from training data; per-language evaluation, more native-speaker labelers, recalibrated thresholds, human review.
- **Bot network evades the classifier within days.** Move to behavior and graph signals that are costly to fake, fast retraining, honeypots, rate limits; treat as ongoing adversarial game.
- **Viral misinformation during an election.** Fast-path human review, reduce distribution while reviewing, fact-checker labels, provenance signals; trade-off: speed vs accuracy vs free expression.

**Vocabulary:** DAU/MAU, engagement, retention cohorts, social graph, feed ranking, integrity, prevalence, coordinated inauthentic behavior, content policy, appeals, DSA, trust & safety.

---

## 6. Search engines

**Use cases:** web/document retrieval, query understanding (spelling, intent, entities), learning to rank, query autocomplete, snippets and answer extraction, AI-generated answers with citations, spam/SEO-spam detection, freshness for news, personalization, image and voice search.

**Data & constraints:** web-scale index (billions of documents), query logs, click logs (biased by position). Latency: < 200-500 ms end to end. Freshness matters for news. Quality judged by human raters plus clicks.

**Business metrics:** nDCG on rated queries, click-through and long-click rate, abandonment (no click), query reformulation rate, time to success, ad revenue, freshness lag.

**Case study: web search with AI answers**
```
Crawler (politeness, priority by importance & freshness) → parse & dedupe → indexer (inverted index + vector index), sharded
Query → spell/intent/entity understanding → retrieval (BM25 + dense) from all shards → merge
     → learning-to-rank (hundreds of features: relevance, quality/authority, freshness, click signals)
     → top results + optional LLM answer generated only from top results with citations
     → logging (clicks, dwell time) → training data (with position-bias correction)
```
- Deep dives: sharding by document and fan-out to all shards, tiered index (hot fresh index vs main index), position bias in click data (randomization or click models), LLM answer must cite sources and avoid hallucination.

**What-ifs:**
- **Spam sites start ranking high.** New SEO trick; add spam classifiers, link analysis (link farms), quality signals, human rater review, manual actions.
- **Results for breaking news are stale.** Freshness tier with fast crawling of news sources, freshness feature in ranker, detect "trending query" intent.
- **AI answer quotes a satire website as fact.** Source quality filters, cross-source agreement, don't show AI answer for low-confidence or sensitive queries.
- **Click-trained ranker keeps promoting the first result.** Position bias; use inverse propensity weighting, randomized interleaving, human relevance labels.

**Vocabulary:** inverted index, BM25, dense retrieval, learning to rank (pointwise/pairwise/listwise), nDCG, position bias, click models, query understanding, crawl budget, PageRank, freshness, interleaving, SERP.

---

## 7. Autonomous vehicles & robotics

**Use cases:** perception (object detection, segmentation, lidar point clouds), sensor fusion, tracking and prediction of other agents, planning and control, mapping and localization, simulation, data mining for rare events, robot grasping and manipulation, warehouse robots.

**Data & constraints:** camera, lidar, radar, IMU, GPS at high frequency; petabytes of driving logs. Latency: hard real-time (tens of milliseconds) **on the vehicle** with limited compute and power. Safety-critical: functional safety standards (ISO 26262, SOTIF). Long tail of rare events matters most.

**Business metrics:** miles per disengagement, collisions per million miles, comfort metrics (hard braking), mission success rate, simulation pass rate, robot pick success rate, throughput per robot.

**Case study: data engine for perception improvement**
```
Fleet vehicles → on-board triggers (model uncertainty, disagreement, driver takeover) → upload interesting clips
   → data lake → auto-labeling (big offline models) + human labeling for hard cases
   → training (multi-task perception) → evaluation on scenario suites + simulation (replay & synthetic edge cases)
   → safety review → model compression (quantization, TensorRT) → over-the-air deployment in shadow mode → full rollout
```
- Deep dives: **long tail** (rare events like a child chasing a ball), active data mining instead of random sampling, offline metrics by scenario category, simulation for things you can't test on roads, shadow mode comparison, redundancy (multiple sensors and fallback behavior).

**What-ifs:**
- **Detection fails in heavy rain/fog.** Under-represented conditions; mine fleet data for weather, augmentation, sensor fusion (radar works in fog), conservative fallback behavior (slow down).
- **New model has better mAP but more hard-braking events.** Offline metric doesn't capture temporal stability; measure tracking consistency, flicker, false positives at short range; evaluate in closed-loop simulation.
- **A new city has different road signs.** Domain shift; collect & label local data, map updates, staged rollout by geography.
- **Robot arm works in the lab but fails in the warehouse.** Lighting, object variety, clutter (sim-to-real gap); domain randomization in simulation, real-world fine-tuning, failure logging and retry policies.

**Vocabulary:** perception, sensor fusion, lidar point cloud, BEV (bird's-eye view), tracking, motion prediction, planning, SLAM, localization, disengagement, ODD (operational design domain), long tail, shadow mode, sim-to-real, ISO 26262, functional safety.

---

## 8. Manufacturing & IoT

**Use cases:** predictive maintenance, visual defect inspection, anomaly detection on sensor streams, process optimization (yield), digital twins, energy optimization, quality prediction, robotics on assembly lines, supply forecasting.

**Data & constraints:** high-frequency sensor time series (vibration, temperature, pressure), images from line cameras, maintenance logs (often handwritten). Edge deployment (factory network, low latency, offline). **Very few failure labels**. Cost of errors: missed defect → recall or safety issue; false stop → stopped production line (expensive).

**Business metrics:** unplanned downtime, OEE (overall equipment effectiveness), defect escape rate, false reject rate, scrap rate, maintenance cost, mean time between failures (MTBF).

**Case study: predictive maintenance for 2,000 machines**
```
Sensors (vibration, temp, current) → edge gateway (filtering, FFT features, buffering if offline)
   → stream to cloud (MQTT → Kafka) → time-series DB + feature store
   → models: anomaly detection (no labels needed) + remaining useful life (RUL) model where failure history exists
   → alerts with confidence & expected time to failure → maintenance work order system
   → technician feedback (real fault? what was replaced?) → labels → retraining
```
- Deep dives: few failures → start with **unsupervised anomaly detection** and physics-based thresholds, label from maintenance logs (NLP on technician notes), per-machine baselines (each machine is different), edge vs cloud split, cost-based alert threshold.

**What-ifs:**
- **Inspection model rejects too many good parts after a lighting change.** Input drift; monitor image statistics, retrain with new lighting, fixed lighting enclosures, normalization.
- **Only 10 examples of a rare defect.** Anomaly detection trained on good parts only (autoencoder, PatchCore), synthetic defects, few-shot learning, human-in-the-loop.
- **Sensor stops sending data and the model says "healthy".** Missing data treated as normal; detect missing/flatlined sensors explicitly and alert on data quality.
- **Technicians don't trust alerts.** Show which sensor and pattern triggered the alert, track precision, start with high-confidence alerts only, include their feedback.

**Vocabulary:** OEE, predictive vs preventive maintenance, RUL, MTBF, SCADA, PLC, MQTT, edge gateway, digital twin, FFT, anomaly detection, yield, scrap rate, false reject, defect escape.

---

## 9. Telecom

**Use cases:** churn prediction, network anomaly and fault detection, capacity planning and traffic forecasting, network optimization (5G resource allocation), customer support chatbots, fraud (SIM swap, subscription fraud), next-best-offer, call center analytics.

**Data & constraints:** call detail records (CDRs), network telemetry at very high volume, customer data. Regulation on customer data and lawful use. Network issues affect millions quickly. Many legacy systems.

**Business metrics:** churn rate, ARPU (average revenue per user), network uptime, dropped call rate, mean time to detect/resolve incidents, NPS, retention campaign ROI.

**Case study: churn prediction + retention**
```
Usage (CDRs), billing, complaints, network quality per customer, contract end date
   → monthly features → churn model (GBDT) → **uplift model** (who will stay *because* of an offer)
   → targeting: offer to customers with high uplift and high value → campaign → measured with control group
```
- Deep dives: predicting churn is not enough; target people who are **persuadable** (uplift), not "sure to leave" or "sure to stay"; always keep a holdout to measure the campaign effect.

**What-ifs:**
- **Retention campaign increased churn.** Contacting some customers reminds them to leave ("sleeping dogs"); uplift modeling fixes this.
- **Network anomaly alerts flood engineers during an outage.** Alert correlation (root-cause grouping by topology), deduplication, severity ranking.
- **SIM-swap fraud rising.** Real-time risk scoring on swap requests (recent password changes, unusual location), step-up verification, block high-risk transactions after a swap.

**Vocabulary:** CDR, ARPU, churn, uplift, NPS, OSS/BSS, RAN, 5G slicing, KPI degradation, SIM swap, next-best-action.

---

## 10. Logistics, supply chain & delivery

**Use cases:** ETA prediction, route optimization, dispatch and matching (drivers ↔ orders, riders ↔ drivers), surge/dynamic pricing, demand forecasting, warehouse slotting and picking, fraud, address correction, delivery time promises.

**Data & constraints:** GPS traces, maps/road graph, orders, traffic, weather. Real-time decisions (seconds). Two-sided marketplace effects. Combination of ML (predictions) and optimization (OR solvers).

**Business metrics:** on-time delivery rate, ETA error (MAE, % late beyond promise), cost per delivery, driver utilization, wait time, cancellation rate, marketplace balance.

**Case study: ETA prediction for food delivery**
```
Order placed → components: restaurant prep time model + driver pickup travel time + drop-off travel time
   features: restaurant load, time of day, weather, live traffic, driver location, historical speeds on road segments
   → ETA model (GBDT or deep model on route segments) → quantile predictions → promise shown to user (conservative quantile)
   → actual times logged → monitoring per city/restaurant → retraining
```
- Deep dives: **asymmetric cost** (being late is worse than early → predict a higher quantile), break ETA into stages, live updates during delivery, feedback loop (ETA promise affects demand).

**What-ifs:**
- **ETAs are accurate on average but very wrong at dinner rush.** Model lacks real-time load features; add live restaurant/driver supply features, segment evaluation by hour.
- **Surge pricing removes demand but driver supply doesn't increase.** Pricing model ignores supply elasticity; measure both sides in experiments; use switchback experiments.
- **A/B test on dispatch algorithm gives weird results.** Marketplace interference (treatment and control share drivers); use switchback (time-based) or geo-based randomization.
- **Hurricane disrupts the supply chain.** Forecast models break; switch to scenario planning, human overrides, rapid re-forecasting with recent data only.

**Vocabulary:** ETA, quantile regression, VRP (vehicle routing problem), dispatch/matching, surge pricing, supply-demand balance, switchback experiments, last mile, OR (operations research), slotting.

---

## 11. Energy & utilities

**Use cases:** load forecasting, renewable generation forecasting (solar, wind), grid anomaly and outage prediction, predictive maintenance of assets (transformers, turbines), energy trading, smart meter analytics, energy theft detection, battery optimization.

**Data & constraints:** smart meter time series, weather data, SCADA, satellite images. Regulated industry, critical infrastructure (security!), forecast errors cost money in balancing markets.

**Business metrics:** forecast error (MAPE, pinball loss), outage minutes (SAIDI/SAIFI), imbalance costs, asset failure rate, renewable curtailment.

**Case study: day-ahead solar generation forecast**
```
Weather forecasts (irradiance, clouds, temperature) + satellite cloud images + historical plant output
   → features per plant & hour → probabilistic model (GBDT quantiles / deep model) → P10/P50/P90 per hour
   → trading & grid balancing decisions → actual output → error monitoring
```
- Deep dives: weather forecast is the biggest error source (use ensembles), probabilistic outputs for risk decisions, new plants (transfer from similar plants).

**What-ifs:**
- **Load forecast fails on a holiday / heat wave.** Missing calendar or extreme-weather data; holiday features, extreme-event training data, human override.
- **Smart meter data has gaps.** Impute carefully, flag estimated values, don't train on imputed values as truth.
- **Theft-detection model flags poor neighborhoods disproportionately.** Fairness review, check proxies, require human inspection before action.

**Vocabulary:** load forecasting, day-ahead market, pinball loss, SCADA, smart meter, SAIDI/SAIFI, curtailment, demand response, grid balancing.

---

## 12. Education (edtech)

**Use cases:** personalized learning paths, knowledge tracing (predict mastery), automated grading and feedback, AI tutors, dropout prediction, content recommendation, plagiarism and AI-writing detection, question generation.

**Data & constraints:** student interaction logs, answers, essays, video engagement. **Minors' data** (COPPA, FERPA, GDPR-K): strict privacy and consent. Fairness across students is critical. Pedagogical correctness matters more than engagement.

**Business metrics:** learning outcomes (test score gain), course completion, retention, time to mastery, teacher time saved, student satisfaction.

**Case study: AI tutor for math**
```
Student question / attempt → guardrails (age-appropriate, safety) → tutor LLM with pedagogy prompt (hint, don't give answer)
   → math verification tool (symbolic solver checks steps) → response
Knowledge tracing model (student mastery per skill) → chooses next problem difficulty
Teacher dashboard (progress, struggling students, flagged conversations)
```
- Deep dives: **don't just give answers** (learning vs convenience), verify math with tools (LLMs make arithmetic mistakes), measure learning gain (pre/post tests, A/B), privacy for children.

**What-ifs:**
- **Students use the tutor to get answers and test scores drop.** Change policy to hints and Socratic questions, limit full solutions, measure learning outcomes not usage.
- **Automated essay grader gives lower scores to non-native writers.** Bias analysis by group, train on diverse essays, human review for borderline, grade content separately from grammar.
- **AI-writing detector falsely accuses students.** Detectors are unreliable; never use as sole evidence; prefer process-based assessment.

**Vocabulary:** knowledge tracing (BKT, DKT), mastery learning, adaptive learning, item response theory (IRT), learning gain, COPPA, FERPA, formative vs summative assessment.

---

## 13. HR tech & recruiting

**Use cases:** resume parsing and matching, candidate ranking, job recommendations, interview scheduling, attrition prediction, skills extraction, salary benchmarking, internal mobility, HR chatbots.

**Data & constraints:** resumes and job descriptions (text), application outcomes, employee data. **High fairness and legal risk**: equal employment laws, NYC bias-audit law for automated hiring tools, EU AI Act classes hiring as high-risk. Historical hiring data contains past bias.

**Business metrics:** time to hire, quality of hire (performance, retention), recruiter productivity, candidate experience, diversity of pipeline, application completion rate.

**Case study: resume-job matching**
```
Job description → skill & requirement extraction (LLM / NER) ─┐
Resume → parsing (layout + NER) → skills, experience, education ─┴→ matching model (embeddings + structured features)
   → ranked candidates with explanations ("matches 7 of 9 required skills")
   → recruiter decision (human always decides) → outcomes → bias audits by group (adverse impact ratio)
```
- Deep dives: remove protected attributes **and proxies** (names, photos, certain schools, gaps), **don't train only on past hiring decisions** (they encode bias), explainable skill-based matching, regular bias audits.

**What-ifs:**
- **Model ranks women lower for engineering roles.** Learned from biased history; audit, remove proxy features, train on skill-match labels instead of past hires, apply fairness constraints, document.
- **Candidates stuff resumes with hidden keywords.** Parse visible text only, semantic matching, keyword-stuffing detection.
- **Attrition model is used to deny promotions.** Misuse of model; define allowed uses, governance, human decision-making, transparency.

**Vocabulary:** ATS (applicant tracking system), adverse impact / four-fifths rule, disparate impact, bias audit, skills taxonomy, quality of hire, EEOC, high-risk AI system.

---

## 14. Legal & compliance

**Use cases:** contract review and clause extraction, legal research (RAG over case law), e-discovery (find relevant documents in litigation), compliance monitoring (communications surveillance), regulatory change tracking, document drafting assistants, due diligence.

**Data & constraints:** long documents, precise language, confidentiality (attorney-client privilege), citations must be **exactly** correct. Hallucinated case law has led to real court sanctions. Explainability and traceability are required.

**Business metrics:** hours saved per review, recall in e-discovery (missing a document is costly), precision of clause extraction, citation accuracy, lawyer adoption.

**Case study: contract review assistant**
```
Contract upload → OCR/layout parsing → clause segmentation → clause classification (indemnity, termination, liability cap…)
   → extraction of key terms (dates, amounts, parties) with structured output → comparison against company playbook
   → risk flags with exact quoted text & location → lawyer review UI (accept / edit) → feedback improves models
```
- Deep dives: **always quote the source text** (no unsupported claims), long-context handling, on-prem or private deployment for confidentiality, high recall for risky clauses, versioned playbooks.

**What-ifs:**
- **Legal research tool cites a case that doesn't exist.** Retrieval-only citations: the model may only cite documents returned by retrieval; verify every citation against the database before showing.
- **E-discovery misses relevant documents.** Measure recall with statistical sampling (elusion test), technology-assisted review with active learning, document the process for court.
- **Different jurisdictions have different rules.** Metadata filter by jurisdiction and date, show which law applies.

**Vocabulary:** e-discovery, TAR (technology-assisted review), privilege, clause extraction, playbook, redlining, jurisdiction, precedent, elusion rate, chain of custody.

---

## 15. Cybersecurity

**Use cases:** intrusion and anomaly detection, malware classification, phishing detection, user behavior analytics (insider threats), alert triage and prioritization, vulnerability prioritization, security copilots (LLM summarizing incidents), bot detection.

**Data & constraints:** logs (network flows, endpoint, authentication), emails, binaries. Huge volume, very few true attacks (extreme imbalance). **Adversarial**: attackers actively evade models. Analyst time is the bottleneck. Model itself is an attack target (poisoning, evasion, prompt injection on security copilots).

**Business metrics:** mean time to detect (MTTD) and respond (MTTR), true-positive rate of alerts, alerts per analyst per day, missed incidents, phishing click rate.

**Case study: alert triage system for a SOC**
```
SIEM alerts (thousands/day) → enrichment (asset criticality, user risk, threat intel)
   → triage model (probability alert is real + severity) → grouping related alerts into incidents (graph)
   → prioritized queue for analysts + LLM summary of incident (with evidence links)
   → analyst verdicts → labels → retraining; automated playbooks for low-risk well-known cases
```
- Deep dives: alert fatigue, labels from analyst verdicts (biased toward what was investigated), adversarial robustness, explainability for analysts, never let the LLM take destructive actions automatically.

**What-ifs:**
- **Attackers bypass the malware classifier with small changes.** Adversarial evasion; ensemble of static + behavioral detection, adversarial training, frequent updates.
- **Anomaly detector flags every new software deployment.** Learn normal change patterns, whitelist known deploy events, context from change management system.
- **Phishing model performance drops when attackers use LLM-written emails.** Shift to sender/infrastructure signals (domain age, authentication SPF/DKIM), URL analysis, not just writing style.
- **Security copilot is prompt-injected via a malicious log line.** Treat log content as untrusted data, read-only tools, human approval for actions.

**Vocabulary:** SIEM, SOC, EDR, IDS/IPS, threat intelligence, IOC, MITRE ATT&CK, MTTD/MTTR, alert fatigue, phishing, zero-day, adversarial evasion, data poisoning, UEBA.

---

## 16. Gaming

**Use cases:** player churn prediction, matchmaking, cheat detection, in-game economy and pricing (offers), content/level recommendation, toxicity detection in chat/voice, game AI (NPC behavior, RL agents for testing), procedural and generative content, LTV prediction.

**Data & constraints:** telemetry events at huge scale, real-time matchmaking (seconds), multiplayer fairness, young players (privacy, safety). Players dislike unfair monetization.

**Business metrics:** retention (D1, D7, D30), DAU, session length, ARPDAU, payer conversion, LTV, match quality, cheat reports, toxicity rate.

**Case study: skill-based matchmaking**
```
Players enter queue → skill rating (Elo / TrueSkill-style, updated after each match) + latency region + party size
   → matcher balances: skill difference, wait time, ping → match formed
   → match outcome → rating update → monitor: win-rate balance (~50%), quit rate, wait time
```
- Deep dives: trade-off between wait time and match fairness (relax constraints over time), new players' uncertain rating, smurf detection (experienced players on new accounts).

**What-ifs:**
- **New cheat spreads and reports spike.** Server-side behavior anomaly detection (impossible aim/speed), rapid rules + model update, delayed ban waves so cheaters can't learn what triggered detection.
- **Personalized offers increase revenue but reviews say "pay to win".** Guardrail metrics on retention and sentiment; fairness rules on offers.
- **Matchmaking wait times are too long at night.** Wider skill window over time, merge regions, bots for low-population periods.

**Vocabulary:** retention D1/D7/D30, ARPDAU, LTV, whales, Elo/TrueSkill/MMR, matchmaking, smurfing, ban wave, telemetry, live ops.

---

## 17. Travel & hospitality

**Use cases:** dynamic pricing / revenue management (hotel rooms, flights), demand forecasting, search ranking for listings, personalized recommendations, fraud (fake listings, stolen cards), review analysis, customer service chatbots, cancellation prediction, overbooking.

**Data & constraints:** booking data (strong seasonality, long lead times), search logs, listing content. External shocks (pandemics, events). Inventory is perishable (an empty room tonight is lost forever).

**Business metrics:** RevPAR (revenue per available room), occupancy, ADR (average daily rate), booking conversion, cancellation rate, customer satisfaction.

**Case study: hotel dynamic pricing**
```
Historical bookings + current bookings on the books (pace) + competitor prices + events + seasonality
   → demand forecast per room type per future date (with uncertainty)
   → price elasticity model → optimizer chooses price to maximize expected revenue (with business rules: min/max, brand)
   → prices published → booking response → model update
```
- Deep dives: booking pace curves, elasticity estimation (you only see bookings at prices you set → needs experiments), overbooking with cancellation probability.

**What-ifs:**
- **A pandemic hits and the model keeps forecasting normal demand.** Regime change; use recent data only, scenario inputs, human overrides, faster retraining.
- **Listing ranking favors big hotels; small hosts complain.** Two-sided marketplace fairness; add exposure/diversity constraints, new-listing boosts.
- **Fake listings scam guests.** Verification, image reverse-search, behavior signals, payment held until check-in.

**Vocabulary:** RevPAR, ADR, occupancy, revenue management, booking pace, lead time, overbooking, price elasticity, OTA, GDS.

---

## 18. Media, entertainment & streaming

**Use cases:** content recommendation, artwork/thumbnail personalization, content tagging (genres, moods, scenes), subtitle generation and translation, dubbing, content demand forecasting (what to license/produce), video quality optimization (encoding), churn prediction, search.

**Data & constraints:** viewing history (implicit feedback), video/audio content, metadata. Large catalog with long tail. Personalization at scale with low latency. Licensing differs by country.

**Business metrics:** hours watched, retention, churn, take rate on recommendations, content discovery (share of long-tail viewed), cost per viewing hour of content, streaming quality (rebuffering rate).

**Case study: home page personalization**
```
Candidate rows (Continue Watching, Trending, Because you watched X, genre rows)
   → per-row candidate titles (collaborative filtering, content embeddings, trending)
   → ranking of titles within rows + ranking of rows on the page (page-level optimization)
   → artwork personalization (bandit selects thumbnail per user)
   → impressions/plays → offline evaluation + A/B tests on retention
```
- Deep dives: page-level optimization (diversity across rows), country licensing filters, evaluation on long-term retention rather than clicks, bandits for artwork.

**What-ifs:**
- **New original show gets low views despite high quality.** Cold start; content-based embeddings, editorial boosts, exploration, trailers.
- **Recommendations become a filter bubble.** Diversity and novelty in ranking, explicit exploration, measure catalog coverage.
- **Auto-generated subtitles have errors in names and slang.** Custom vocabulary, human review for top content, quality metrics (WER) by language.

**Vocabulary:** implicit feedback, take rate, catalog coverage, filter bubble, artwork personalization, contextual bandits, ASR/WER, adaptive bitrate, rebuffering.

---

## 19. Agriculture

**Use cases:** crop yield prediction, plant disease detection from photos, precision spraying (weed detection on machines), irrigation optimization, satellite/drone imagery analysis, livestock monitoring, commodity price forecasting, soil analysis.

**Data & constraints:** satellite and drone images, weather, soil sensors, farm records. Seasonal (one data point per season per field → slow learning). Poor connectivity in fields (edge/offline). Huge geographic variation.

**Business metrics:** yield per hectare, input cost (water, fertilizer, pesticide) reduction, disease detection accuracy, farmer adoption, prediction error at harvest.

**Case study: plant disease detection app for farmers**
```
Farmer takes a photo (mobile, often offline) → on-device small CNN (quantized) → disease + confidence
   → if low confidence: queue photo to upload later → cloud model / agronomist review
   → recommendation in local language (treatment, when to consult expert) → feedback → retraining
```
- Deep dives: offline-first mobile model, local languages and low literacy (voice, icons), regional differences in crops and diseases, photos taken in bad conditions.

**What-ifs:**
- **Model trained on lab leaf photos fails on field photos.** Domain shift (background, light, multiple leaves); collect field photos, augmentation, segmentation of the leaf first.
- **Yield model trained in one country fails in another.** Different crops, climate, practices; local data, transfer learning, per-region calibration.
- **Cloud cover blocks satellite images during key weeks.** Radar satellites (SAR) see through clouds, temporal interpolation, fusion with weather data.

**Vocabulary:** NDVI, remote sensing, multispectral imagery, SAR, precision agriculture, variable-rate application, phenology, yield gap.

---

## 20. Government & public sector

**Use cases:** document processing (forms, permits), citizen service chatbots, tax fraud detection, benefits eligibility, public health surveillance, traffic management, policy analysis with NLP, translation services, defense and intelligence applications.

**Data & constraints:** sensitive citizen data, strict procurement and security requirements (on-prem, sovereign cloud, certifications), **high accountability**: decisions affect people's rights, must be explainable and appealable, public scrutiny. EU AI Act classifies many public uses as high-risk. Legacy systems and paper records.

**Business metrics:** processing time per application, backlog size, error rate, citizen satisfaction, fraud recovered, cost savings, equity of outcomes across groups.

**Case study: benefits application processing**
```
Application (web or scanned paper) → document AI (OCR + field extraction) → validation against registries
   → eligibility rules engine (law encoded as rules, not ML) + ML risk score for fraud review (only to prioritize review)
   → human caseworker makes the decision → decision letter with reasons → appeal process
   → audits: fairness by group, error rates, published transparency report
```
- Deep dives: **ML prioritizes, humans decide**, rules for legal eligibility, transparency and appeal, bias audits, data minimization.

**What-ifs:**
- **Fraud model wrongly flags thousands of families** (this happened in real scandals). Severity: stop automated actions, human review, compensate; root cause: biased features (nationality, income proxies), no human oversight; prevent: impact assessments, audits, appeal rights.
- **Chatbot gives wrong legal information to citizens.** Ground answers only in official sources with links, disclaimers, easy handoff to a human, monitor and correct.
- **Data cannot leave the country.** Sovereign cloud or on-prem deployment, open-weight models hosted locally.

**Vocabulary:** EU AI Act (high-risk systems), algorithmic impact assessment, transparency register, due process, appeal, data minimization, sovereign cloud, FedRAMP, accessibility (WCAG).

---

## 21. Which chapters to study for each industry

| Industry | Most relevant chapters |
|---|---|
| Healthcare & life sciences | [07](07-ml-fundamentals.md), [10](10-computer-vision.md), [09](09-nlp-and-llms.md), [11](11-statistics-and-ab-testing.md), [13](13-mlops.md) |
| Banking / finance / insurance | [07](07-ml-fundamentals.md), [05 #5](05-case-studies.md#5-real-time-fraud-detection), [04 C](04-what-if-scenarios.md#c-ml-models-in-production), [11](11-statistics-and-ab-testing.md) |
| E-commerce & retail | [05 #4, #6](05-case-studies.md), [04 F](04-what-if-scenarios.md#f-recommenders-search--ranking), [11](11-statistics-and-ab-testing.md) |
| Advertising & marketing tech | [07 §7](07-ml-fundamentals.md#7-evaluation--metrics), [11](11-statistics-and-ab-testing.md), [02](02-ml-and-llm-systems.md) |
| Social media & content | [05 #4, #7](05-case-studies.md), [04 F](04-what-if-scenarios.md#f-recommenders-search--ranking), [09](09-nlp-and-llms.md) |
| Search engines | [05 #6](05-case-studies.md#6-semantic-search-for-e-commerce), [02 §7](02-ml-and-llm-systems.md#7-llm-systems-rag-in-depth), [09](09-nlp-and-llms.md) |
| Autonomous vehicles & robotics | [10](10-computer-vision.md), [08](08-deep-learning.md), [13](13-mlops.md) |
| Manufacturing & IoT | [07 §6](07-ml-fundamentals.md#6-unsupervised-learning), [10](10-computer-vision.md), [13](13-mlops.md) |
| Telecom | [07](07-ml-fundamentals.md), [11](11-statistics-and-ab-testing.md), [01](01-fundamentals.md) |
| Logistics & delivery | [07](07-ml-fundamentals.md), [11](11-statistics-and-ab-testing.md), [01](01-fundamentals.md) |
| Energy & utilities | [07](07-ml-fundamentals.md), [13](13-mlops.md) |
| Education | [09](09-nlp-and-llms.md), [02](02-ml-and-llm-systems.md), [11](11-statistics-and-ab-testing.md) |
| HR tech & recruiting | [09](09-nlp-and-llms.md), [07 §9](07-ml-fundamentals.md#9-what-if-scenarios), [04 #29](04-what-if-scenarios.md#29-model-is-biased-against-a-user-group) |
| Legal & compliance | [02 §7](02-ml-and-llm-systems.md#7-llm-systems-rag-in-depth), [04 A](04-what-if-scenarios.md#a-rag-systems), [05 #1](05-case-studies.md#1-enterprise-rag-assistant-multi-tenant) |
| Cybersecurity | [07](07-ml-fundamentals.md), [04 #15](04-what-if-scenarios.md#15-prompt-injection-a-user-made-the-bot-reveal-its-system-prompt--ignore-rules), [01 §7](01-fundamentals.md#part-7-reliability-monitoring-security) |
| Gaming | [11](11-statistics-and-ab-testing.md), [07](07-ml-fundamentals.md), [01](01-fundamentals.md) |
| Travel & hospitality | [05 #4, #6](05-case-studies.md), [11](11-statistics-and-ab-testing.md) |
| Media & streaming | [05 #4](05-case-studies.md#4-recommendation-system), [04 F](04-what-if-scenarios.md#f-recommenders-search--ranking), [11](11-statistics-and-ab-testing.md) |
| Agriculture | [10](10-computer-vision.md), [13](13-mlops.md) |
| Government & public sector | [02 §11](02-ml-and-llm-systems.md#11-safety-security--governance), [05 #8](05-case-studies.md#8-document-ai-pipeline), [04 #29](04-what-if-scenarios.md#29-model-is-biased-against-a-user-group) |

**Final tip:** before any interview, read this company's industry section, then prepare **one sentence** for each of these: the cost of errors, the main regulation, the latency need, and where labels come from. Use them in your first two minutes.
