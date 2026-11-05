# 04 — 50 "What If…?" Scenarios with Model Answers

Every answer follows the framework from [03-debugging-framework.md](03-debugging-framework.md):
**Causes (ranked) → How to isolate → Fix (now / long-term) → Prevent.**

**How to practice:** read only the question, cover the rest, speak for 3 minutes, then compare. Mark the ones you missed and redo them 2 days later.

### Contents
- [A. RAG systems (1–12)](#a-rag-systems)
- [B. LLM apps & agents (13–22)](#b-llm-apps--agents)
- [C. ML models in production (23–32)](#c-ml-models-in-production)
- [D. Data & pipelines (33–38)](#d-data--pipelines)
- [E. Serving, infra & scale (39–46)](#e-serving-infra--scale)
- [F. Recommenders, search & ranking (47–50)](#f-recommenders-search--ranking)

---

## A. RAG systems

### 1. Same question, different answers for different users (or on retry)
*Full worked answer in [03-debugging-framework.md](03-debugging-framework.md#full-worked-example--the-question-you-were-asked).*
**Short version:** temperature/sampling → per-user prompt differences (history, ACLs) → non-deterministic retrieval (ANN, ties, query rewrite) → version skew (index/model/prompt) → conflicting docs → cache.
**Isolate:** replay N times, log chunk IDs + prompt hash + model version. Same chunks + different answers = generation. Different chunks = retrieval.
**Fix:** temp 0 + pinned model, deterministic tie-breaks, versioned index with atomic swap, dedupe conflicting docs, version in cache key.
**Prevent:** consistency eval (agreement over N runs), log versions per request.

### 2. RAG says "I don't know" even though the answer is in the documents
**Causes (ranked):**
1. Document never indexed properly — PDF parse failure, scanned image without OCR, table flattened into garbage.
2. Chunking split the answer across chunks, or chunk too big so the embedding is diluted.
3. Vocabulary mismatch — user says "PTO", doc says "paid leave". Pure vector search misses exact terms, codes, IDs.
4. Similarity threshold too strict / top-k too small.
5. Metadata filter wrong (wrong tenant, date filter, ACL).
6. Answer retrieved but ranked low → cut off by reranker or context budget.
7. Prompt too strict ("only answer if 100% sure").

**Isolate:** search the vector DB directly for the doc → is it there? Inspect the chunk text. Run the query and print top-50 with scores — where does the right chunk rank? If not in top-50 → embedding/chunking. In top-50 but not top-5 → reranking/k.
**Fix:** better parser/OCR, chunk with overlap & respect headings, **hybrid search (BM25 + vector)**, query expansion/rewrite, raise k then rerank, tune threshold on labeled set.
**Prevent:** retrieval eval set with **recall@k**, ingestion validation (empty-chunk checks, parse-success rate).

### 3. RAG gives confident wrong answers (hallucinations)
**Causes:** retrieved chunks are irrelevant but model answers anyway; model uses its own pretrained knowledge; outdated docs; prompt doesn't require grounding; conflicting chunks.
**Isolate:** check if the answer text is supported by retrieved chunks (groundedness / faithfulness check). Classify failures: *retrieval failure* (right doc not retrieved) vs *generation failure* (right doc retrieved, model ignored it).
**Fix:** prompt "answer only from context, cite sources, say I don't know otherwise"; require citations and verify cited chunk contains the claim; reranker + relevance threshold; smaller context with higher precision; post-hoc NLI/LLM-judge faithfulness check before returning.
**Prevent:** faithfulness metric in evals (e.g., RAGAS-style), user feedback thumbs-down loop, hallucination rate dashboard.

### 4. Answers are outdated after the source docs were updated
**Causes:** ingestion pipeline not triggered / failing silently; old chunks not deleted (upsert adds new, old stays → both retrieved); answer cache not invalidated; embedding batch job lags.
**Isolate:** compare doc `last_modified` vs. index `ingested_at`; search index for both old and new versions of the doc.
**Fix:** change-data-capture (event on doc update) → re-ingest; **delete-by-doc_id then insert** (idempotent upserts keyed by doc_id + chunk_no); cache key includes index version; prefer newest via `effective_date` metadata.
**Prevent:** freshness SLO ("95% of doc updates searchable in < 15 min"), alert on ingestion lag.

### 5. Retrieval quality dropped after switching embedding model
**Cause:** almost always — **query embedded with new model, documents still embedded with old model** (different vector spaces) or partially re-embedded index. Also: different normalization (cosine vs dot product), different max token length truncating chunks.
**Fix:** re-embed entire corpus into a **new index**, test offline, then swap atomically. Never mix models in one index. Store `embedding_model_version` as index metadata and assert at query time.
**Prevent:** retrieval eval gate before swap.

### 6. RAG is too slow (p95 = 8 s)
**Isolate first:** trace per stage. Typical budget: embed 20 ms, retrieve 30–100 ms, rerank 100–300 ms, LLM first token 300–800 ms, full generation 1–5 s.
**Fixes by stage:**
- LLM: **stream tokens** (perceived latency), smaller/faster model for simple queries (routing), shorter context, limit output tokens, prompt caching, speculative decoding/self-hosted vLLM.
- Retrieval: ANN index (HNSW) tuning, fewer filters post-hoc, colocate DB.
- Rerank: rerank top-20 not top-100, smaller cross-encoder.
- Query rewrite: skip it for short clear queries, or run in parallel.
- Cache: exact-match + **semantic cache** for frequent questions.
- Parallelize independent calls (retrieve from 2 sources concurrently).
**Trade-off:** latency vs quality — measure quality impact of each cut on eval set.

### 7. Users see documents they shouldn't have access to
**Severity: security incident** — say so. Mitigate immediately (disable feature or restrict to safe corpus).
**Causes:** ACL filtering done *after* retrieval in the app (bug) or not at all; ACL metadata stale (permission revoked but index not updated); shared cache across users returns another user's answer; prompt injection asking to "show all docs".
**Fix:** enforce **pre-retrieval filtering** in the vector DB with tenant/group IDs; per-tenant namespaces/indexes for strong isolation; cache key includes user/permission scope; sync ACL changes on events.
**Prevent:** automated tests "user A queries doc B → must not appear", audit logs.

### 8. Works great in demo, bad in production
**Causes:** eval set doesn't represent real queries (demo questions were written by the team who know the docs); real users write short, vague, misspelled, multi-language queries; production corpus 100× bigger → more distractors.
**Fix:** sample real production queries → label → new eval set; add query rewriting/clarifying questions; hybrid search; reranker; slice metrics by query type.
**Prevent:** continuous eval on sampled production traffic.

### 9. Answer quality is fine for short docs, bad for long docs (100+ page manuals)
**Causes:** fixed-size chunks lose structure; tables/sections split; "lost in the middle" — LLMs ignore middle of long context.
**Fix:** structure-aware chunking (by headings), parent-child retrieval (retrieve small chunk, give parent section), add doc title/section path to each chunk, summarise sections, put most relevant chunks at start/end of context.

### 10. Multi-hop questions fail ("Which manager approved the project that had the biggest budget?")
**Cause:** single retrieval can't fetch both facts.
**Fix:** query decomposition (LLM splits into sub-questions), iterative/agentic retrieval, knowledge graph for entity relations, or SQL tool for structured data.
**Trade-off:** more LLM calls = more latency and cost.

### 11. Cost of RAG app exploded this month
**Isolate:** cost per request × requests; break down tokens: input (context!) vs output; which feature/user/tenant.
**Causes:** context size grew (k raised, longer chunks, chat history unbounded); retries loop; one tenant / bot abusing; agent loops; more expensive model in use.
**Fix:** token budget per request, summarise history, model routing (cheap model for easy queries), semantic cache, prompt caching, per-user rate limits & quotas, max-iterations on agents.
**Prevent:** cost per request dashboard + budget alerts.

### 12. Different answers in English vs Hindi (or other language) for the same question
**Causes:** embedding model weak at cross-lingual retrieval; docs only in English; LLM weaker in that language.
**Fix:** multilingual embedding model; translate query → retrieve in doc language → answer in user's language; eval per language.

---

## B. LLM apps & agents

### 13. The model suddenly got worse, and we didn't change anything
**Causes:** provider updated the model behind an alias (`gpt-x-latest`); our data/docs changed; user traffic mix changed (new customer, new feature); a dependency (tokenizer, SDK default params) changed; system prompt edited via config by another team.
**Isolate:** rerun golden eval set now vs. stored results; check model version in response headers/logs; diff prompt/config history.
**Fix:** pin dated model versions; version prompts in git; rollback.
**Prevent:** daily scheduled eval run against production config; alert on score drop.

### 14. The model sometimes returns invalid JSON and breaks the downstream service
**Fix (layered):** use structured output / JSON mode / function calling with schema; validate with a schema (Pydantic); on failure → retry with the error message ("fix this JSON"); fallback default; temperature 0; keep schema small.
**Prevent:** parse-failure rate metric; contract tests.

### 15. Prompt injection: a user made the bot reveal its system prompt / ignore rules
**Explain:** direct injection (user input) vs **indirect injection** (malicious text inside retrieved doc/web page/email).
**Mitigate:** never trust LLM output for authorization; least-privilege tools (read-only by default, human approval for actions like send/delete/pay); separate system vs. untrusted content clearly; input/output classifiers; don't put secrets in prompts; allow-listed tool arguments.
**Key line:** *"I assume the model WILL be tricked, so I design the system so a tricked model can't do damage."*

### 16. Agent gets stuck in a loop calling the same tool
**Causes:** tool returns error the model doesn't understand; ambiguous tool descriptions; no stopping criterion.
**Fix:** max-steps + max-cost limits, detect repeated identical calls, clear error messages from tools, better tool descriptions, planner/executor split, return partial result + escalate to human.

### 17. LLM provider is down / rate limiting us (429s)
**Mitigate:** retries with exponential backoff + jitter; **fallback to a second provider/model** via an LLM gateway; queue non-urgent requests; graceful degradation ("Answers delayed").
**Long-term:** multi-provider gateway, quota management per feature, circuit breaker, self-hosted backup model for critical paths.

### 18. Chatbot forgets earlier parts of a long conversation
**Cause:** history truncated to fit context window.
**Fix:** rolling summary of older turns + last N turns verbatim; store facts in memory store (vector or key-value) and retrieve relevant ones; per-session state in Redis.

### 19. How do you know your LLM feature is actually good? (evaluation)
**Answer layers:** (1) offline golden set with references → exact-match/semantic similarity, LLM-as-judge with rubric (calibrated against human labels), (2) RAG-specific: context recall/precision, faithfulness, answer relevance, (3) online: thumbs up/down, resolution rate, escalation-to-human rate, A/B tests, (4) safety: red-team set, toxicity, PII leakage.
**Gotcha:** LLM judges are biased (position, verbosity, self-preference) → randomize order, validate against humans.

### 20. Outputs contain PII (emails, phone numbers) of other customers
**Mitigate:** output PII filter now. **Root causes:** PII in indexed docs, or in fine-tuning data (model memorized it), or shared cache/memory across users.
**Fix:** PII redaction at ingestion, tenant isolation, cache scoping, data retention policies, remove from training data and retrain.

### 21. Fine-tuned model is great on our eval but users say it's worse at general tasks
**Cause:** catastrophic forgetting / overfitting to narrow data; eval set too narrow; eval leak (test examples in train).
**Fix:** mix general data in fine-tuning, LoRA with lower rank/lr, fewer epochs, evaluate on general benchmark too, deduplicate train/test. Ask: "Did we even need fine-tuning, or would RAG/prompting work?"

### 22. Responses are too long / verbose and users complain
**Fix:** explicit length instruction + examples, `max_tokens`, output format constraints, eval metric for length, post-processing summarizer as last resort.

---

## C. ML models in production

### 23. Model accuracy was 95% offline but 70% in production
**Causes (ranked):**
1. **Train/serve skew** — features computed differently online vs offline (different code, units, defaults for nulls, timezones).
2. **Data leakage** in training — a feature that wouldn't be available at prediction time (e.g., "refund_issued" when predicting fraud). Offline score was fake.
3. **Distribution shift** — production population differs from training data.
4. Wrong split — random split on time-series data (future leaked into training).
5. Preprocessing mismatch — different tokenizer/scaler version, label encoding order.
**Isolate:** log production features → recompute the same rows offline → compare feature-by-feature. Check feature importance for suspiciously strong features.
**Fix:** single feature definition shared by training & serving (**feature store**), time-based splits, point-in-time correct joins.
**Prevent:** skew monitoring, shadow deployment before launch.

### 24. Model performance slowly degrades over months
**Cause:** **data drift** (input distribution changes) or **concept drift** (relationship between input and label changes, e.g., fraud patterns evolve).
**Detect:** monitor input feature distributions (PSI, KL divergence), prediction distribution, and actual performance when labels arrive (often delayed!).
**Fix:** scheduled retraining or drift-triggered retraining, sliding window training data, online learning for fast-moving domains.

### 25. Model's predictions suddenly all the same (e.g., everything "not fraud")
**Causes:** upstream feature broken → all nulls → default value; a feature service down and returning fallback; model file corrupted/wrong version deployed; input scaling bug.
**Isolate:** check prediction distribution & feature null rates around the time it started; correlate with deploys.
**Fix:** rollback; fail loudly (alert) instead of silently defaulting.
**Prevent:** input validation, alerts on prediction distribution, canary deploys.

### 26. Labels arrive 30 days late (e.g., loan default, chargebacks). How do you monitor?
**Answer:** use proxy signals until labels arrive — input drift, prediction drift, early indicators (first payment missed), human-reviewed sample. Then backfill real performance when labels land.

### 27. Fraud model: 99.9% accuracy but catches no fraud
**Cause:** class imbalance — predicting "not fraud" always is 99.9% accurate.
**Fix:** use precision/recall, PR-AUC, recall at fixed false positive rate; class weights, resampling, threshold tuning based on business cost (cost of missed fraud vs. cost of blocking good user).

### 28. New model won the offline evaluation but lost the A/B test
**Causes:** offline metric ≠ business metric; offline data biased by old model (it only saw items the old model showed — **selection bias / feedback loop**); latency increase hurt engagement; novelty effects; A/B test underpowered.
**Fix:** align offline metric to online goal, counterfactual/off-policy evaluation, check guardrail metrics (latency), run test longer/with power analysis.

### 29. Model is biased against a user group
**Isolate:** slice metrics by group (FPR, FNR per group). **Causes:** under-representation in training data, proxy features (zip code ≈ race), biased historical labels.
**Fix:** rebalance/collect data, remove proxies, fairness constraints, per-group thresholds (with legal review), human review for high-stakes.

### 30. Retraining pipeline produced a worse model and it auto-deployed
**Fix:** **never auto-deploy without gates**: eval against current champion on fixed holdout + recent data, sanity checks (prediction distribution), canary with automatic rollback. Model registry with champion/challenger.

### 31. Can't reproduce last month's model
**Need:** version everything — code (git), data snapshot (DVC/Delta/lakehouse time travel), features, hyperparameters, random seeds, library versions (Docker image), experiment tracking (MLflow/W&B).

### 32. Model works in batch, but real-time version is different
**Cause:** batch features use full-day aggregates; real-time uses partial windows; different code paths.
**Fix:** same feature definitions (feature store, streaming computation), point-in-time features, compare outputs on the same entities.

---

## D. Data & pipelines

### 33. A daily pipeline silently produced half the usual rows
**Fix/prevent:** data quality checks (row counts vs expected range, null rates, schema, freshness) that **fail the pipeline** (Great Expectations / dbt tests), alerting, idempotent reruns.

### 34. Upstream team changed a column type and broke our model
**Fix:** data contracts (schema agreed and validated at boundary), schema registry, version columns instead of mutating, CI tests on upstream changes.

### 35. Duplicate events in Kafka caused double-counting
**Explain:** most queues give *at-least-once* delivery. **Fix:** idempotent consumers (dedupe by event_id with TTL store), idempotent writes (upsert by key), exactly-once semantics where supported.

### 36. Training data has labeling errors
**Fix:** inter-annotator agreement, label review on disagreements, confident learning (find examples the model strongly disagrees with), gold questions for labelers.

### 37. Backfill job overloaded the production database
**Fix:** read from replica/warehouse not primary, rate-limit batch jobs, run off-peak, separate OLTP and analytics.

### 38. Embedding / ingestion job takes 3 days for the full corpus
**Fix:** parallelize with workers on a queue, batch embedding calls, GPU batching, incremental updates only (hash content → skip unchanged), checkpoint & resume.

---

## E. Serving, infra & scale

### 39. Model latency p99 spikes every few minutes
**Causes:** garbage collection pauses, autoscaling cold starts (model loading), noisy neighbour on GPU, batch jobs sharing the cluster, large inputs, cache expiry thundering herd.
**Fix:** keep warm replicas / min instances, preload models, dynamic batching with max wait, separate pools for batch vs online, timeout + fallback.

### 40. Traffic goes 10× during a product launch
**Plan:** horizontal autoscaling on stateless servers, queue + backpressure, rate limiting & priority tiers, cache hot results, pre-warm capacity, graceful degradation (smaller model, cached answers), load test beforehand.

### 41. GPU cost is too high for LLM inference
**Fix:** continuous batching (vLLM/TGI), quantization (INT8/INT4), smaller distilled model, routing easy queries to small model, KV cache/prefix caching, spot instances for batch workloads, autoscale to zero for low traffic, right-size GPUs.

### 42. One replica returns different predictions than others
**Cause:** mid-rollout with mixed versions, stale model file on one node, different hardware/library version, local cache.
**Fix:** immutable versioned model artifacts, readiness checks that verify model hash, version in response header.

### 43. Rolled out a new model, error rate jumped — what now?
**Answer:** rollback first (that's why we canary + keep previous version warm), then debug from logs offline. "Mitigate first, investigate second."

### 44. Vector DB is the bottleneck at 50M vectors
**Fix:** shard by tenant/hash, tune HNSW (M, ef), use IVF-PQ/quantization to cut memory, metadata pre-filter partitions, replicas for read throughput, tiered storage (hot/cold).

### 45. A downstream feature service is slow, making all predictions slow
**Fix:** timeouts + defaults for non-critical features, circuit breaker, cache features, precompute batch features, async calls in parallel.

### 46. Users in another region experience high latency
**Fix:** deploy in multiple regions, route by geo-DNS, replicate read data/indexes, edge cache, smaller models at edge. Trade-off: consistency of data across regions.

---

## F. Recommenders, search & ranking

### 47. Recommendations show the same popular items to everyone
**Cause:** popularity bias + feedback loop; cold-start fallback used too often; candidate generation too narrow.
**Fix:** diversity/novelty in re-ranking, exploration (bandits, epsilon-greedy), personalization features, debias training with exposure weighting.

### 48. New users / new items get bad recommendations (cold start)
**Fix:** content-based features (item text/image embeddings), onboarding questions, popularity within segment, contextual features (location, device), explore budget for new items.

### 49. Search results are relevant but click-through is dropping
**Isolate:** UI change? latency? new content mix? query distribution shift? **Fix:** check position bias in training data, freshness features, A/B test ranker, analyze zero-click queries.

### 50. Users found the recommender is gaming engagement (clickbait rising)
**Cause:** optimizing a proxy (clicks) not the true goal (satisfaction). **Fix:** multi-objective ranking (dwell time, return visits, hides/reports as negatives), quality classifiers, long-term holdout metrics.

---

## Final drill — 10 rapid-fire questions (answer in 30 seconds each)

1. Same chunks retrieved, different answers → *generation randomness / prompt diff*
2. Different chunks retrieved for the same query → *ANN non-determinism, query rewrite, index version, filters*
3. Great offline, bad online → *train/serve skew, leakage, drift*
4. Slow degradation → *drift → monitor + retrain*
5. Sudden drop → *something changed → correlate with deploys/data*
6. All predictions identical → *broken feature upstream*
7. Provider down → *retry, fallback provider, circuit breaker*
8. Answer is outdated → *ingestion lag, old chunks not deleted, cache*
9. Data leak between users → *security incident, pre-filter ACLs, scoped cache*
10. Cost spike → *token breakdown, context growth, loops, abuse → budgets + routing + cache*
