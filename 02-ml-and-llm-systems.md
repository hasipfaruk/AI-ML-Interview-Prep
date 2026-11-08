# 02. ML & LLM Systems: How They're Actually Built

The interviewer for an AI/ML role wants to see you think **beyond the model**: data, serving, evaluation, monitoring, cost.

> **Keep this in mind:** in production ML, the model is ~10% of the system. The other 90% is data pipelines, serving, monitoring and feedback loops.

### Contents
1. [The ML lifecycle](#1-the-ml-lifecycle)
2. [Data & features](#2-data--features)
3. [Training infrastructure](#3-training-infrastructure)
4. [Model serving](#4-model-serving)
5. [Deployment & experimentation](#5-deployment--experimentation)
6. [Monitoring ML systems](#6-monitoring-ml-systems)
7. [LLM systems: RAG in depth](#7-llm-systems-rag-in-depth)
8. [LLM serving & optimization](#8-llm-serving--optimization)
9. [Agents & tool use](#9-agents--tool-use)
10. [Evaluation of LLM systems](#10-evaluation-of-llm-systems)
11. [Safety, security & governance](#11-safety-security--governance)
12. [Decision tables (when to use what)](#12-decision-tables)

---

## 1. The ML lifecycle
```
Problem framing → Data collection → Labeling → Feature engineering → Training → Evaluation
       ↑                                                                          │
       └── Monitoring ← Serving ← Deployment (canary/shadow) ← Model registry ←───┘
                 │
                 └── feedback / new labels → retraining
```
**Problem framing questions (ask these in every ML design interview):**
- What is the business goal? What is the ML objective (proxy)? Are they aligned?
- Is ML even needed? (Rules/heuristics baseline first.)
- Online (real-time) or batch prediction? Latency budget?
- Where do labels come from? How delayed are they?
- What's the cost of a false positive vs false negative?

## 2. Data & features
- **Feature store** = one place to define features, used by both training (offline store, historical, point-in-time correct) and serving (online store, low latency, e.g., Redis). **Main reason: prevents train/serve skew.**
- **Point-in-time correctness:** when building training rows, only use feature values that existed *at that time*. Otherwise you get leakage.
- **Batch features** (computed daily: "user's purchases last 30 days") vs **real-time features** (streaming: "transactions in last 5 minutes").
- **Data validation:** schema, null rates, ranges, distribution checks before training.
- **Data versioning:** DVC, Delta Lake/Iceberg time travel.
- **Labeling:** human labelers, weak supervision, implicit feedback (clicks), LLM-assisted labeling + human review.

## 3. Training infrastructure
- Orchestration: Airflow / Kubeflow / Prefect / SageMaker pipelines.
- Experiment tracking: MLflow, Weights & Biases.
- Distributed training: **data parallel** (copy model, split data; DDP), **model/tensor parallel** (split model across GPUs), **pipeline parallel**, **FSDP/ZeRO** (shard optimizer state + params). Mixed precision (bf16).
- Checkpointing (resume after spot instance preemption).
- **Model registry:** versioned artifacts + metadata + stage (staging/production).

## 4. Model serving
| Mode | When | Example |
|------|------|---------|
| **Batch** | Predictions can be precomputed | nightly recommendations, churn scores |
| **Online (real-time)** | Need fresh prediction per request | fraud check at payment |
| **Streaming** | Predict on events as they arrive | anomaly detection on logs |
| **On-device / edge** | Privacy, offline, low latency | keyboard prediction |

Serving stack: model server (Triton, TorchServe, TF Serving, BentoML, vLLM for LLMs) behind an API, autoscaling, **dynamic batching** (group requests to use GPU efficiently), model caching.
Optimization: quantization, distillation, pruning, ONNX/TensorRT compilation.

**Two-stage pattern (search/recs/ads):** cheap **candidate generation** (millions → 1000s, e.g., ANN on embeddings) → expensive **ranking** model (1000s → 100) → **re-ranking** with business rules (diversity, freshness).

## 5. Deployment & experimentation
- **Shadow mode** → **canary** → **A/B test** → full rollout. Keep previous model warm for instant rollback.
- **A/B testing:** randomize by user, pick primary metric + guardrail metrics (latency, errors, revenue), power analysis for sample size, beware novelty effect and peeking.
- **Multi-armed bandits** when you want to explore + exploit continuously.
- **Champion / challenger** for automated retraining.

## 6. Monitoring ML systems
| Layer | What to monitor |
|-------|-----------------|
| System | latency, throughput, errors, GPU/CPU/memory |
| Data | missing values, schema, feature distributions (**data drift**: PSI, KS test) |
| Model | prediction distribution, confidence, **performance when labels arrive** (concept drift) |
| Business | conversion, fraud losses, user satisfaction |
Alert → investigate → retrain/rollback. Retraining triggers: schedule, drift threshold, performance drop.

---

## 7. LLM systems: RAG in depth

**RAG (Retrieval-Augmented Generation)** = fetch relevant knowledge, put it in the prompt, let the LLM answer grounded in it.
Use RAG when knowledge changes, is private, or needs citations. (Fine-tuning teaches *style/format/behavior*, not fresh facts.)

### Offline: ingestion pipeline
```
Sources (PDF, Confluence, DB, web) → Connectors → Parse (OCR, tables, layout)
 → Clean (remove boilerplate, dedupe) → Chunk → Enrich metadata (title, section, date, ACL, tenant)
 → Embed → Upsert into vector index (+ keyword index) → Version the index
```
**Chunking choices:**
| Strategy | Notes |
|----------|-------|
| Fixed size (e.g., 500 tokens, 50 overlap) | Simple baseline |
| Recursive / by structure (headings, paragraphs) | Better coherence, usually the best default |
| Semantic chunking | Split where topic changes |
| Parent-child / small-to-big | Retrieve small precise chunk, send bigger parent section to LLM |
| Per table row / per FAQ item | Structured content |
Add **contextual headers** to each chunk: "Doc: HR Policy 2025 > Section: Leave > ...". This improves retrieval a lot.

### Online: query pipeline
```
Query → guardrails → (rewrite / expand / decompose / HyDE) → embed
 → hybrid retrieval (vector + BM25) with metadata/ACL pre-filter → merge (RRF)
 → rerank (cross-encoder) → top-k → build context (order, dedupe, token budget)
 → prompt (instructions + context + question + cite sources) → LLM → output guardrails + citation check → stream to user
```
**Key techniques to name:**
- **Hybrid search**: vectors capture meaning, BM25 captures exact words (product codes, names). Combine with **Reciprocal Rank Fusion**.
- **Reranking**: cross-encoder scores (query, chunk) pairs jointly; big precision boost.
- **Query rewriting**: turn "what about for contractors?" into a standalone query using chat history.
- **HyDE**: generate a hypothetical answer, embed it, search with that.
- **Multi-query**: generate several phrasings, union results.
- **Metadata filtering**: tenant, permissions, date, doc type. Pre-filter for security.
- **GraphRAG / knowledge graphs**: for entity-relationship and multi-hop questions.
- **Agentic RAG**: LLM decides when/what to retrieve iteratively.

### Vector DB essentials
- Similarity: cosine / dot product / L2 (normalize vectors for cosine).
- ANN indexes: **HNSW** (high recall, fast, RAM heavy), **IVF** (cluster then search nearby clusters), **PQ** (compress vectors, less memory, lower recall). ANN = *approximate* → results can vary slightly. This matters for consistency questions.
- Scaling: sharding, replicas, namespaces per tenant, quantization.
- Choice: pgvector (already on Postgres, < ~10M vectors), managed (Pinecone), self-hosted (Milvus, Qdrant, Weaviate), Elasticsearch/OpenSearch (if you need hybrid in one system).

## 8. LLM serving & optimization
| Technique | What it does |
|-----------|--------------|
| **Streaming (SSE)** | Show tokens as they are generated, so the wait feels shorter |
| **Continuous batching** (vLLM, TGI) | New requests join the batch mid-generation → much higher GPU throughput |
| **PagedAttention / KV cache** | Efficient memory for attention cache |
| **Prefix / prompt caching** | Reuse computation for repeated system prompts/context |
| **Quantization** (INT8/INT4, AWQ, GPTQ) | Smaller memory, faster, slight quality loss |
| **Speculative decoding** | Small draft model proposes tokens, big model verifies |
| **Distillation** | Train small model to mimic big one |
| **Model routing / cascade** | Cheap model first; escalate hard queries to big model |
| **Semantic cache** | Return cached answer for similar question |
| **LLM gateway** | One internal API: auth, rate limits, quotas per team, fallback providers, logging, cost tracking |

**Key metrics:** TTFT (time to first token), TPOT/ITL (time per output token), throughput (tokens/s), cost per 1k requests.
**Memory rule of thumb:** params × bytes (FP16 = 2 B) + KV cache. 70B FP16 ≈ 140 GB → multiple GPUs (tensor parallel) or quantize.

**API vs self-hosted:**
| API (closed models) | Self-hosted (open models) |
|---|---|
| Best quality, zero infra, fast start | Data control, cost at high volume, customizable |
| Per-token cost, rate limits, vendor changes | GPU ops burden, scaling, lower top-end quality |

## 9. Agents & tool use
Agent loop: **LLM plans → calls a tool → observes result → repeats → final answer.**
Design concerns: tool schemas & descriptions, max steps/cost limits, state/memory, error handling, **human-in-the-loop for risky actions**, sandboxing code execution, observability of each step, evaluation of trajectories (did it pick the right tools?), permissions per tool (least privilege).
Patterns: ReAct, plan-and-execute, router + specialist agents, multi-agent (use only when you need it; more agents means more failure points).

## 10. Evaluation of LLM systems
| Level | Metrics / methods |
|-------|-------------------|
| Retrieval | recall@k, precision@k, MRR, nDCG (needs labeled query→doc pairs) |
| Generation | faithfulness/groundedness, answer relevance, correctness vs reference, citation accuracy |
| Consistency | agreement rate across repeated runs / paraphrased questions |
| Safety | jailbreak success rate, toxicity, PII leakage |
| Online | thumbs up/down, resolution rate, escalation rate, retention, latency, cost |
Methods: golden datasets (built from real queries), LLM-as-judge (with rubric, validated vs humans), human review of samples, A/B tests, **regression evals in CI on every prompt/model change**.

## 11. Safety, security & governance
- Input guardrails: prompt-injection detection, topic restriction, PII detection.
- Output guardrails: toxicity, PII, policy, schema validation, groundedness.
- **Indirect prompt injection** via retrieved docs/web/email. Treat all retrieved content as untrusted.
- Multi-tenant isolation (separate namespaces, ACL pre-filter, scoped caches).
- Data retention, audit logs, model cards, compliance (GDPR right-to-be-forgotten → must delete from index **and** caches **and** logs; hard for fine-tuned weights → another reason to prefer RAG).

## 12. Decision tables

**Prompting vs RAG vs fine-tuning**
| Need | Use |
|------|-----|
| Fresh/private facts, citations | **RAG** |
| Specific output style/format, domain jargon, smaller cheaper model | **Fine-tuning** (often LoRA) |
| Quick iteration, general task | **Prompt engineering** first, always |
| Both knowledge + behavior | RAG + fine-tuning |

**Real-time vs batch prediction**
| Real-time | Batch |
|-----------|-------|
| Depends on request-time context (fraud at checkout) | Inputs known in advance (daily recs) |
| Harder: latency, online features | Easier, cheaper, can use big models |

**Which metric?**
| Problem | Metric |
|---------|--------|
| Imbalanced classification | precision/recall, PR-AUC, F1 |
| Ranking | nDCG, MRR, recall@k |
| Regression | MAE / RMSE |
| Business | revenue, retention, CTR (with guardrails) |
