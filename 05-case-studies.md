# 05. Case Studies: Full Interview Answers

Each case follows the same 7-step structure you should use in the interview (see [06-interview-playbook.md](06-interview-playbook.md)):

> **1. Requirements → 2. Estimates → 3. API → 4. High-level design → 5. Data model → 6. Deep dives → 7. What-ifs & trade-offs**

### AI/ML cases
1. [Enterprise RAG assistant (multi-tenant)](#1-enterprise-rag-assistant-multi-tenant) (most asked)
2. [Customer-support AI agent](#2-customer-support-ai-agent)
3. [LLM gateway / internal LLM platform](#3-llm-gateway--internal-llm-platform)
4. [Recommendation system (video/product feed)](#4-recommendation-system)
5. [Real-time fraud detection](#5-real-time-fraud-detection)
6. [Semantic search for e-commerce](#6-semantic-search-for-e-commerce)
7. [Content moderation system](#7-content-moderation-system)
8. [Document AI pipeline (invoices/forms extraction)](#8-document-ai-pipeline)

### Classic cases (also asked to AI engineers)
9. [URL shortener](#9-url-shortener)
10. [Chat application](#10-chat-application)
11. [Rate limiter](#11-rate-limiter)

---

## 1. Enterprise RAG assistant (multi-tenant)
> "Design a ChatGPT-like assistant that answers questions over each company's internal documents."

**1. Requirements**
- Functional: upload/connect docs (PDF, Confluence, Drive), ask questions in chat, answers with citations, follow-up questions, respect document permissions, admin sees usage.
- Non-functional: answers grounded (low hallucination), p95 time-to-first-token < 2 s, strict tenant isolation, docs searchable within 15 min of update, 99.9% availability, cost control.

**2. Estimates**: 500 companies × 2,000 users × 10 questions/day = 10M/day ≈ 115 QPS avg, ~350 peak. 500 tenants × 200k docs × 20 chunks = 2B chunks → 2B × 3 KB (768-dim fp32) ≈ 6 TB → shard + quantize. Tokens: 10M × 4k ≈ 40B tokens/day → **cost is the #1 concern** → caching, routing.

**3. API**
```
POST /v1/sources                     connect a source / upload file → returns job_id
GET  /v1/jobs/{id}                   ingestion status
POST /v1/conversations               create chat
POST /v1/conversations/{id}/messages { "text": "..." } → SSE stream of tokens + citations
POST /v1/messages/{id}/feedback      { "rating": -1, "comment": "..." }
```

**4. High-level design**
```
                     ┌──────────────── INGESTION (async) ─────────────────┐
Sources/connectors → │ Queue → Parser/OCR → Chunker → Embedder (GPU batch) │ → Vector DB (sharded by tenant)
  (webhooks / CDC)   │                                   → Keyword index    │ → Object store (raw docs)
                     └────────────────────────────────────────────────────┘ → Metadata DB (Postgres: docs, ACLs, versions)

User → API gateway (auth, tenant, rate limit) → Chat service
          Chat service → Conversation store (history)
                       → Query rewriter (small LLM)
                       → Retriever (hybrid, ACL pre-filter by tenant + groups)
                       → Reranker
                       → Context builder (token budget)
                       → LLM gateway (routing, fallback, caching) → LLM providers / self-hosted vLLM
                       → Output guardrails + citation verification
                       → SSE stream to user
          All steps → Tracing/logging (versions, chunk IDs, tokens, cost) → Eval & monitoring
```

**5. Data model**
- `documents(doc_id, tenant_id, source, title, version, updated_at, acl_groups[], status)`
- `chunks(chunk_id, doc_id, tenant_id, text, section_path, embedding, acl_groups[], index_version)`
- `conversations(conv_id, user_id, tenant_id)` / `messages(msg_id, conv_id, role, text, citations, model_version, prompt_version, index_version, latency, tokens)`

**6. Deep dives**
- **Tenant isolation:** namespace per tenant in vector DB (or index per large tenant); every query has mandatory `tenant_id` filter enforced server-side; ACL groups as pre-filter; cache keys include tenant + permission scope.
- **Freshness:** connectors push change events → re-ingest only changed docs (content hash) → delete old chunks by doc_id → insert new. Full re-embeds (model change) build a new index version and swap alias.
- **Quality:** hybrid search + rerank; contextual chunk headers; "answer only from context with citations"; verify citations; say "I don't know" when retrieval confidence is low.
- **Latency:** streaming, parallel retrieval, rerank only top-30, small model for query rewrite, prompt caching.
- **Cost:** semantic cache for repeated questions per tenant, model routing (simple → small model), context budget, per-tenant quotas.
- **Evaluation:** per-tenant golden sets from real queries; retrieval recall@k, faithfulness, consistency; thumbs-down sampling to human review; CI eval gate on prompt/model changes.

**7. What-ifs** → see scenarios 1-12 in [04-what-if-scenarios.md](04-what-if-scenarios.md). Be ready for: inconsistent answers, no answer, data leakage between tenants, outdated answers, embedding model migration, provider outage.

---

## 2. Customer-support AI agent
> "Design an AI agent that resolves support tickets: answers questions, checks order status, issues refunds."

- **Requirements:** chat + email channels, answer FAQs (RAG over help center), take actions via tools (order lookup, refund ≤ $50), hand off to human, audit trail. Non-functional: safe actions, < 3 s responses, measurable resolution rate.
- **Design:**
```
Channel adapters → Conversation service → Intent classifier/router
   ├─ FAQ → RAG pipeline
   ├─ Action → Agent (LLM + tools: get_order, create_refund, update_address)
   │            Tools behind a Tool API with authZ (acts AS the customer, not admin), limits, idempotency keys
   │            Risky actions (refund > $50) → human approval queue
   └─ Escalation → Human agent console (with AI summary of conversation)
State: conversation store + ticket system;  Observability: trace every tool call
```
- **Deep dives:** idempotent refunds (idempotency key per ticket), policy checks done in code not in prompt, max-steps limit, prompt-injection defense (user can't make it refund $5,000 because the tool enforces limits), evaluation via simulated customers + replay of historical tickets, metrics: resolution rate, CSAT, escalation rate, wrong-action rate.
- **What-ifs:** agent loops (#16), injection (#15), tool API down (fallback to human), duplicate refund (idempotency).

---

## 3. LLM gateway / internal LLM platform
> "Many teams in our company want to use LLMs. Design a platform."

- **Requirements:** one API for many models/providers, auth per team, quotas & cost attribution, logging/redaction, fallback, caching, eval & prompt management.
- **Design:**
```
Teams' apps → LLM Gateway (stateless, autoscaled)
                 ├─ AuthN/Z (API keys per team), PII redaction
                 ├─ Rate limiter (tokens/min per team, Redis token bucket)
                 ├─ Router (model by policy/cost/latency; fallback on 429/5xx; circuit breaker)
                 ├─ Cache (exact + semantic)
                 ├─ Providers: external APIs, self-hosted vLLM cluster (GPU autoscaling)
                 └─ Async logging → Kafka → warehouse (usage, cost per team) + trace store
Prompt registry (versioned prompts) | Eval service (run suites on new model/prompt versions)
```
- **Trade-offs:** central gateway adds a hop (~ms) and is a critical dependency → deploy multi-AZ, keep it thin. Streaming support required end to end.

---

## 4. Recommendation system
> "Design the home feed recommendations for a video app with 100M users."

- **Requirements:** personalized feed, fresh content, < 200 ms, optimize long-term engagement (watch time, not just clicks), diversity.
- **Estimates:** 100M DAU × 20 feed loads = 2B/day ≈ 23k QPS avg, ~70k peak. 10M candidate videos.
- **Design (multi-stage funnel):**
```
Request → Candidate generation (≈1000 items, parallel sources):
              ├─ Two-tower model: user embedding → ANN search over video embeddings
              ├─ Collaborative filtering / co-watch
              ├─ Trending / fresh / followed creators
          → Ranking model (≈1000 → 100): deep model with user, item, context features; multi-task (P(click), P(watch>50%), P(like), P(hide))
          → Re-ranking (business rules): diversity, freshness, dedupe, remove watched, policy filters
          → Feed
Features: online feature store (Redis) ← streaming (Kafka/Flink: recent watches) + batch (Spark daily)
Training: logged impressions + engagement → daily/continuous training → registry → canary → A/B test
```
- **Deep dives:** cold start (#48), popularity bias & exploration (#47), position bias in logged data, multi-objective scoring (`score = w1·P(watch) + w2·P(like) − w3·P(hide)`), precomputing for inactive users (batch) vs real-time for active.
- **What-ifs:** offline win/online loss (#28), clickbait (#50), feature pipeline lag → stale recommendations.

---

## 5. Real-time fraud detection
> "Score every card transaction for fraud in < 100 ms."

- **Requirements:** score at authorization time, block/allow/review decision, explainability for analysts, adapt to new fraud patterns. 10k TPS peak.
- **Design:**
```
Payment service → Fraud API (p99 < 100ms)
     ├─ Rules engine (hard blocks: blacklisted card, impossible velocity)
     ├─ Feature fetch: online store (Redis): real-time aggregates (txns in last 5 min, new device?, distance from last txn)
     │      ↑ Streaming pipeline (Kafka → Flink) updates aggregates per card/user/merchant
     ├─ Model (GBDT e.g. XGBoost: fast, strong on tabular; maybe + graph features for fraud rings)
     └─ Decision: score → thresholds (allow / step-up auth (OTP) / block / manual review queue)
Labels: chargebacks (delayed 30-90 days), analyst reviews → training data (point-in-time features)
```
- **Deep dives:** class imbalance (#27), delayed labels (#26), threshold set by business cost, **fail-open vs fail-closed** if fraud service is down (usually fail-open with rules-only fallback for small amounts; state the trade-off), adversarial drift (#24), explainability (SHAP for analysts).

---

## 6. Semantic search for e-commerce
> "Users type 'comfortable running shoes for flat feet'. Return relevant products."

- **Design:** query understanding (spell-fix, category/attribute extraction with an LLM or classifier: category=running shoes, feature=arch support) → **hybrid retrieval** (BM25 on title/attributes + vector search on product embeddings) with filters (in stock, price, size) → learning-to-rank model (features: text relevance, popularity, CTR, conversion, price, personalization) → re-rank (diversity, sponsored slots).
- Indexing: product catalog changes → CDC → update search index (Elasticsearch/OpenSearch with vector support).
- Evaluation: nDCG on labeled query-product pairs, online CTR / add-to-cart / zero-result rate.
- What-ifs: zero results (#2 analog: query relaxation, fallbacks), position bias (#49), new products cold start (#48).

---

## 7. Content moderation system
> "Detect harmful posts (text + images) on a social platform with 50M posts/day."

- **Design:**
```
Post created → sync fast check (hash match against known-bad content, cheap text classifier) → publish or hold
             → async deeper models via queue (multimodal classifiers / LLM with policy prompt)
             → score per policy category → auto-remove (high confidence) | human review queue (uncertain) | allow
User reports → priority boost into review queue
Human decisions → labels → retraining; appeals flow
```
- **Deep dives:** precision vs recall per category (CSAM: maximize recall; satire: precision), cost (cheap model filters, expensive model only for uncertain), multilingual, adversarial evasion (leetspeak, text in images → OCR), reviewer wellbeing & throughput, latency of the async path.

---

## 8. Document AI pipeline
> "Extract fields from 1M invoices/month (vendor, date, total, line items)."

- **Design:** upload → object storage → queue → classify doc type → OCR/layout model (or multimodal LLM) → field extraction (structured output with JSON schema) → validation rules (totals sum, date formats, vendor in master data) → confidence score → auto-approve or human review UI → corrections stored as training data → ERP via API.
- **Estimates:** 1M/month ≈ 0.4/s average, so throughput is easy; focus on accuracy, cost per document, and review workload.
- **What-ifs:** new invoice layout breaks extraction (drift → human review rises → retrain/few-shot examples), scanned low-quality docs (pre-processing, OCR confidence), duplicate invoices (hash + business key dedupe), LLM returns invalid JSON (#14).

---

## 9. URL shortener
- **Req:** shorten URL, redirect fast, 100M new URLs/month, read-heavy (100:1).
- **Estimates:** writes ≈ 40/s, reads ≈ 4k/s; 5 years × 1.2B × 500 B ≈ 3 TB.
- **Design:** `POST /shorten` → ID generator (Snowflake or counter ranges per server) → **base62 encode** (7 chars = 62⁷ ≈ 3.5T) → store `code → long_url` in key-value DB (DynamoDB/Cassandra). `GET /{code}` → cache (Redis) → DB → **301/302 redirect**. Analytics via async events to Kafka.
- **Trade-offs:** hash vs counter (collisions vs coordination), 301 (cached by browser, less analytics) vs 302.

## 10. Chat application
- **Req:** 1:1 & group chat, online status, delivery receipts, history.
- **Design:** clients hold **WebSocket** connections to chat servers; connection registry (Redis: user → server); message → chat server → persist (Cassandra, partitioned by conversation_id, sorted by time) → route to recipient's server via pub/sub; offline users → push notification; message IDs time-sortable (Snowflake) for ordering.
- **Deep dives:** at-least-once delivery + client dedupe, group fan-out, presence via heartbeats, end-to-end encryption.

## 11. Rate limiter
- **Design:** token bucket per (user, endpoint) stored in Redis with atomic Lua script; at API gateway; return 429 + `Retry-After`. For LLM: limit tokens/min and concurrent requests.
- **Trade-offs:** centralized Redis (accurate, extra hop) vs local in-memory (fast, approximate); fail-open if Redis down.
