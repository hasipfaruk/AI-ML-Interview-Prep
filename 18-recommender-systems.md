# 18 — Recommender Systems (Deep Dive)

Asked at e-commerce, streaming, social media, food delivery, ads, news, jobs and dating companies — one of the most common ML system design topics.
For a full design answer see [05-case-studies.md](05-case-studies.md#4-recommendation-system).

### Contents
1. [Basics](#1-basics)
2. [Collaborative filtering & matrix factorization](#2-collaborative-filtering--matrix-factorization)
3. [Content-based & hybrid](#3-content-based--hybrid)
4. [The multi-stage architecture](#4-the-multi-stage-architecture)
5. [Candidate generation: two-tower & ANN](#5-candidate-generation-two-tower--ann)
6. [Ranking models & features](#6-ranking-models--features)
7. [Training data, negatives & losses](#7-training-data-negatives--losses)
8. [Sequential & real-time recommendation](#8-sequential--real-time-recommendation)
9. [Evaluation](#9-evaluation)
10. [Bias, feedback loops & exploration](#10-bias-feedback-loops--exploration)
11. [Re-ranking & multi-objective](#11-re-ranking--multi-objective)
12. [What-if scenarios (recommenders)](#12-what-if-scenarios)

---

## 1. Basics

**Q: What does a recommender system do?** Predicts which items (products, videos, songs, jobs) a user will find valuable, and ranks them. Business goals: engagement, conversion, retention, revenue, discovery.

**Q: Explicit vs implicit feedback?** Explicit: ratings, likes (rare, clear meaning). Implicit: clicks, watch time, purchases, skips (plentiful, noisy, no true negatives — "not clicked" may mean "not seen").

**Q: Main approaches?** Popularity-based, collaborative filtering (users who liked X also liked Y), content-based (item attributes), hybrid, deep learning (two-tower, sequence models), knowledge/graph-based, and bandits/RL for exploration.

**Q: What is the user-item interaction matrix?** Rows = users, columns = items, values = interactions. It's extremely **sparse** (users interact with a tiny fraction of items).

## 2. Collaborative filtering & matrix factorization

**Q: User-based vs item-based collaborative filtering?** User-based: find similar users, recommend what they liked. Item-based: find items similar to ones the user liked (based on co-interaction). Item-based is more stable (item similarities change slowly) and easier to precompute — used by Amazon early on.

**Q: Similarity measures?** Cosine, Pearson correlation, Jaccard (for binary interactions).

**Q: Matrix factorization?** Approximate the interaction matrix R ≈ U·Vᵀ, where each user and item gets a low-dimensional vector (embedding). Predicted score = dot product. Train with SGD or **ALS** (alternating least squares — scales well, good for implicit data).

**Q: Implicit-feedback MF?** Treat all interactions as positive with confidence weights (more views → more confidence), unobserved as weak negatives (Hu-Koren-Volinsky). Or use ranking losses (BPR).

**Q: Weaknesses of collaborative filtering?** Cold start (new users/items have no interactions), popularity bias, sparsity, can't use content/context features directly.

**Q: Factorization Machines (FM)?** Model pairwise interactions between all features (user, item, context) with factorized weights — generalizes MF to include side features. Extensions: FFM, DeepFM.

## 3. Content-based & hybrid

**Q: Content-based recommendation?** Represent items by features (text, category, image embeddings, tags) and recommend items similar to what the user consumed. Works for new items; risk: over-specialization (only "more of the same").

**Q: How do you create item embeddings from content?** Text encoders (sentence embeddings of title/description), image encoders (CLIP), audio embeddings, or LLM-generated attribute tags.

**Q: Hybrid systems?** Combine CF and content signals — e.g., content features as inputs to a two-tower model, or blend scores. Best of both: personalization + cold-start handling.

**Q: Can LLMs be used in recommendation?** Yes: generating item descriptions/tags, embeddings, conversational recommendation, explaining recommendations, re-ranking small candidate sets, and generative retrieval. Main limits: latency and cost at large scale, so usually used offline or at the last stage.

## 4. The multi-stage architecture

**Q: Why multiple stages?** You can't run a heavy model on millions of items per request within 100–200 ms. So you narrow down step by step:
```
All items (10M)
  → Candidate generation / retrieval (≈ 1,000)   cheap: ANN on embeddings, co-occurrence, popular, followed
  → (Light pre-ranking (≈ 300))                  small model
  → Ranking (≈ 100)                              heavy model with rich features
  → Re-ranking / business logic (≈ 20 shown)     diversity, freshness, dedupe, ads, policy filters
```
**Q: Why multiple candidate sources?** Each captures different intent: personalized embeddings, "because you watched X", trending, new items, followed creators, location-based. Merging them increases recall and diversity.

**Q: Online vs offline computation?** Precompute item embeddings and some user candidates offline (batch). Compute user embedding, retrieval and ranking online for freshness. Inactive users can get fully precomputed lists.

## 5. Candidate generation: two-tower & ANN

**Q: What is a two-tower model?** A **user tower** (user features + history → embedding) and an **item tower** (item features → embedding). Score = dot product. Trained so that interacted pairs score high.
**Why it's popular:** item embeddings are precomputed and indexed in an ANN index; at request time compute one user embedding and search → millisecond retrieval over millions of items.

**Q: Limitations of two-tower?** No feature interaction between user and item before the final dot product → less accurate than a ranking model. That's why it's used for retrieval, not final ranking.

**Q: ANN indexes for retrieval?** HNSW, IVF, ScaNN, FAISS. Trade-off recall vs latency vs memory. Refresh index as new items arrive (incremental updates or frequent rebuilds). See [02 §7](02-ml-and-llm-systems.md#7-llm-systems-rag-in-depth).

**Q: Other retrieval methods?** Item-to-item co-occurrence ("bought together"), graph-based (random walks — PinSage), rule-based (trending in your city), and search queries.

## 6. Ranking models & features

**Q: Ranking model types?** Logistic regression → GBDT → deep models: **Wide & Deep**, **DeepFM**, **DCN** (deep & cross network), **DIN** (attention over user history relative to the candidate item), multi-task models (**MMoE**, PLE) predicting several outcomes at once.

**Q: What does the ranking model predict?** Probabilities of actions: P(click), P(watch > 30 s), P(purchase), P(like), P(share), P(hide/skip). Final score combines them (see §11).

**Q: Feature categories?**
| Type | Examples |
|---|---|
| User | age bucket, country, device, long-term interests, embeddings |
| Item | category, price, age of item, quality score, creator, embeddings |
| User × item | past interactions with this creator/category, similarity between user and item embeddings |
| Context | time of day, day of week, location, session length, page |
| Real-time | last 10 items viewed, clicks in this session |
| Counters | item CTR last 1 h / 24 h, popularity trend |

**Q: How to handle high-cardinality IDs?** Embedding tables (hashing trick to cap size), frequency thresholds, shared embeddings, mixed-dimension embeddings.

**Q: Why calibrate ranking scores?** When combining multiple predictions or using them in auctions (ads), probabilities must be accurate, not only correctly ordered. Negative downsampling during training distorts probabilities → recalibrate.

## 7. Training data, negatives & losses

**Q: Where do labels come from?** Logged impressions with outcomes: shown and clicked = positive; shown and not clicked = negative (for ranking). Only items **shown** get labels → selection bias.

**Q: Negative sampling for retrieval?**
- **Random negatives:** cheap, easy negatives (model learns popular vs unpopular).
- **In-batch negatives:** other users' positives in the batch — efficient but biased toward popular items → apply **logQ correction**.
- **Hard negatives:** items similar to positives but not engaged — improve precision; too hard → false negatives.
- Mix of easy + hard is common.

**Q: Losses?**
| Loss | Use |
|---|---|
| Binary cross-entropy (pointwise) | CTR prediction in ranking |
| **BPR** (pairwise) | score(positive) > score(negative) for implicit feedback |
| **Sampled softmax** | retrieval — positive vs many sampled negatives |
| Listwise (LambdaRank, softmax over list) | optimize ranking metrics like nDCG |
| Contrastive / InfoNCE | two-tower training |

**Q: Point-in-time correctness?** Features must be computed as they were at impression time (e.g., item CTR at that moment), otherwise leakage. Log features at serving time and train on them.

## 8. Sequential & real-time recommendation

**Q: Sequence-aware models?** Treat user history as a sequence and predict the next item: GRU4Rec (RNN), **SASRec** (self-attention, causal), BERT4Rec (masked items), Transformers with side features. Capture order and short-term intent ("watching a series in order").

**Q: Session-based recommendation?** For anonymous users or short sessions: use the items clicked in the current session only (session-kNN, GRU4Rec).

**Q: Real-time personalization architecture?**
```
User events → Kafka → stream processor (Flink) → update online features (recent items, counters) in Redis
Request → fetch fresh features → retrieval + ranking → response
```
Also: update user embedding online (from recent items) without retraining, near-real-time training (hourly incremental updates).

**Q: Generative recommenders?** Large sequence models trained on user action sequences (and semantic item IDs) that generate the next items directly — an active trend at large companies.

## 9. Evaluation

**Q: Offline metrics?**
- Retrieval: **Recall@K**, hit rate@K.
- Ranking: **nDCG@K**, MAP, MRR, AUC / GAUC (AUC per user, averaged), log loss.
- Beyond accuracy: coverage (% catalog recommended), diversity, novelty, serendipity, popularity bias.

**Q: Offline evaluation protocol?** Time-based split (train on past, test on future), never random split. Leave-last-out per user for sequential models. Evaluate on all candidates or a fair sample (sampled metrics can mislead).

**Q: Online evaluation?** A/B tests with primary metric (watch time, purchases, retention) + guardrails (latency, diversity, complaints, creator-side metrics). **Interleaving** (mix results from two rankers in one list, see which gets more clicks) — needs 10–100× less traffic to detect a winner, good for fast ranker iteration.

**Q: Why do offline and online results disagree?** Logged data only contains items the old model showed (selection bias); offline metrics ignore position effects, diversity, freshness, latency; short-term clicks ≠ long-term satisfaction. See [04 #28](04-what-if-scenarios.md#28-new-model-won-the-offline-evaluation-but-lost-the-ab-test).

**Q: Counterfactual/off-policy evaluation?** Use logged propensities with IPS or doubly robust estimators to estimate a new policy's performance offline. See [16 §6](16-reinforcement-learning.md#6-model-based-offline--imitation-learning).

## 10. Bias, feedback loops & exploration

**Q: Types of bias?**
| Bias | Meaning | Mitigation |
|---|---|---|
| **Position bias** | items at top get clicked more just because of position | position as feature during training (set fixed at serving), inverse propensity weighting, randomization experiments |
| **Popularity bias** | popular items get recommended more, get more data, get even more popular | logQ correction, re-ranking for long tail, exposure fairness |
| **Selection/exposure bias** | only shown items have labels | exploration traffic, IPS weighting |
| **Conformity / presentation bias** | UI influences behavior | careful logging, experiments |

**Q: What is a feedback loop?** The model decides what users see → users interact only with that → training data reflects the model's own choices → model reinforces itself, reducing diversity (filter bubble).

**Q: Exploration methods in recsys?** Reserve a small % of slots for exploration (ε-greedy), bandits (Thompson sampling for new items), boost new items with uncertainty bonuses, randomized holdout traffic for unbiased data.

## 11. Re-ranking & multi-objective

**Q: How to combine multiple objectives?** Weighted score: `score = w1·P(click) + w2·E[watch time] + w3·P(like) − w4·P(hide)`; tune weights with online experiments; or constrained optimization (maximize engagement subject to diversity/quality constraints); Pareto-optimal tuning.

**Q: Diversity in re-ranking?** **MMR** (maximal marginal relevance — trade relevance against similarity to already-picked items), DPP (determinantal point processes), category caps ("max 2 items from same creator in top 10").

**Q: Other re-ranking rules?** Remove already-purchased/watched, dedupe near-duplicates, freshness boosts, policy/safety filters, business rules (sponsored slots, inventory availability), fairness for creators/sellers.

---

## 12. What-if scenarios

Already covered in [04-what-if-scenarios.md](04-what-if-scenarios.md#f-recommenders-search--ranking): popular items for everyone (#47), cold start (#48), CTR dropping (#49), clickbait optimization (#50). More below.

### Users complain "it only shows me the same type of content" (filter bubble)
**Causes:** feedback loop; ranking only optimizes short-term engagement; no diversity constraints; retrieval sources too narrow (all from user's top category).
**Isolate:** measure diversity per user (unique categories in top 20), compare over time; check share of candidates from each source.
**Fix:** diversity in re-ranking (MMR, category caps), exploration slots, add "explore" candidate source, long-term satisfaction objectives (retention, survey responses), user controls ("show less like this").
**Prevent:** diversity and novelty as guardrail metrics in A/B tests.

### Recommendations are stale after a big event (breaking news, a viral video, a new season launched)
**Causes:** batch pipeline updates daily; item embeddings missing for new items (not in ANN index yet); popularity counters computed hourly; model trained on last week.
**Fix:** streaming features (real-time counters), incremental ANN index updates, a "trending now" candidate source, content-based embeddings for new items available immediately, more frequent incremental training.
**Prevent:** monitor "time from item creation to first recommendation" and share of fresh items shown.

### Offline Recall@K improved a lot, but online metrics didn't move
**Causes:** ranking stage throws away the new candidates anyway (retrieval wasn't the bottleneck); offline eval biased toward items the old system showed; improvement concentrated in items users don't care about; latency increased.
**Isolate:** check how many new candidates survive ranking and get shown; evaluate end-to-end (retrieval + ranking) offline; slice by user activity.
**Fix:** joint evaluation of the full funnel, retrain ranker with new candidates (ranker must see them in training), improve logging of exposure.

### Embedding table is too large for memory (hundreds of millions of users/items)
**Fix:** hashing trick (with collisions), frequency-based pruning (rare IDs share a bucket), mixed-dimension embeddings (popular IDs get larger vectors), quantization (fp16/int8), sharded embedding servers (parameter servers / TorchRec), replace user ID embeddings with history-based user towers (compute user vector from recent items → no per-user table).

### The same item appears multiple times (or near-duplicates fill the feed)
**Causes:** multiple candidate sources return the same item; same content uploaded several times (re-posts, different IDs); variants of a product (colors/sizes).
**Fix:** dedupe by item ID after merging sources; content hashing / embedding similarity to cluster near-duplicates; group product variants; diversity rules in re-ranking.

### A new ranking model increased clicks but decreased purchases/retention
Optimizing the wrong proxy. Use multi-task objectives with downstream outcomes (purchase, return visits), weight by value, add guardrail metrics, run longer tests to see long-term effects (holdouts).

### Recommendations look great for heavy users, terrible for light users
**Causes:** model dominated by heavy users' data; light users have few features.
**Fix:** per-segment evaluation, GAUC, content/context features, popular-in-segment fallback, onboarding signals, separate model or features for light users.

### Latency of the recommendation API is above the 200 ms budget
Trace per stage. Fix: cache user embeddings and candidate lists, reduce candidates to the ranker, pre-ranking stage, model distillation/quantization, feature fetch batching, parallel candidate sources with timeouts (drop a slow source instead of waiting).

### Sellers/creators complain they get no exposure
Popularity bias and rich-get-richer. Add exposure fairness constraints, new-creator boosts with exploration, monitor exposure distribution (Gini coefficient), creator-side metrics in experiments.

### Model suddenly recommends inappropriate items to children/sensitive users
Policy filters missing in re-ranking for that surface, new items not yet classified, features for age missing. Fix: hard filters by policy before ranking, default to safe when classification is pending, audit logging.
