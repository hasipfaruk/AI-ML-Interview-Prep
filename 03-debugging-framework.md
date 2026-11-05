# 03 — The Debugging Framework (How to Answer "What If X Happens?")

This is the most important file. Interviewers ask scenario questions because they want to see **how you think**, not whether you
memorized the answer. A calm, structured answer with an imperfect conclusion beats a list of random guesses every time.

---

## The framework: **C.L.H.I.F.P.**

> **C**larify → **L**ayer map → **H**ypotheses → **I**solate (measure) → **F**ix (now + long-term) → **P**revent

| Step | What you do | What you say |
|------|-------------|--------------|
| **1. Clarify** | Pin down the symptom. Who, when, how often, since when, what changed? | "Before I jump in — is this for *all* users or some? Started suddenly or gradually? Did we deploy anything recently?" |
| **2. Layer map** | Draw the request path. Every layer is a suspect. | "Let me walk the request path: query → rewrite → embed → retrieve → rerank → prompt → LLM → post-process." |
| **3. Hypotheses** | List causes per layer, **ranked by likelihood**. | "The most likely causes, in order, are: sampling temperature, retrieval non-determinism, and index version mismatch." |
| **4. Isolate** | How you'd *prove* which one it is, cheapest test first. | "I'd replay the same query 20 times and log retrieved chunk IDs. If chunks are identical but answers differ → it's generation. If chunks differ → it's retrieval." |
| **5. Fix** | Short-term mitigation + long-term fix. | "Short-term: temperature 0 and pin the model version. Long-term: versioned index with atomic swaps." |
| **6. Prevent** | Monitoring, evals, alerts, tests so it doesn't recur. | "I'd add a consistency eval to CI and alert when answer agreement drops below 90%." |

**Memory trick:** *"Can Large Hippos Itch For Pizza?"*

---

## Step 2 in detail — the layer maps

You must be able to draw these from memory. When asked any scenario, **draw the relevant one first**.

### RAG / LLM application
```
User
 │
 ▼
[API gateway / auth / rate limit]
 │
 ▼
[Conversation memory]  ← chat history, user profile
 │
 ▼
[Query understanding]  ← rewrite, expand, classify intent, guardrails (input)
 │
 ▼
[Embedding model]      ← query → vector
 │
 ▼
[Retriever]            ← vector DB (ANN) + keyword (BM25) + metadata/ACL filters
 │
 ▼
[Reranker]             ← cross-encoder, top-k selection
 │
 ▼
[Context builder]      ← order chunks, truncate to token budget, add citations
 │
 ▼
[Prompt template]      ← system prompt + context + question
 │
 ▼
[LLM]                  ← model version, temperature, max tokens, provider
 │
 ▼
[Post-processing]      ← guardrails (output), format, citation check
 │
 ▼
[Cache]  [Logs/traces]  [Feedback]
```
**Offline side (where many bugs live):**
```
Source docs → parse/OCR → clean → chunk → embed → upsert to vector index → (index version)
```

### Classic ML model in production
```
Raw data → ETL → Feature pipeline → Feature store (offline + online)
                                         │                 │
                                    Training job       Serving API ← request
                                         │                 │
                                    Model registry ──► Model server → prediction → logging → monitoring
```

### Generic web service
```
Client → DNS → CDN → Load balancer → App servers → Cache → Database
                                         │
                                       Queue → Workers
```

---

## Step 3 in detail — universal causes checklist

When you're stuck, run through these. One of them is almost always the answer.

| Category | Questions to ask yourself |
|----------|--------------------------|
| **Change** | What was deployed / changed? Code, model, prompt, data, config, dependency, provider? |
| **Data** | Did the input data change (drift, schema, nulls, new source, stale)? |
| **Randomness** | Is anything non-deterministic (sampling, ANN search, GPU math, random seeds, ties)? |
| **State** | Is there per-user state (history, cache, personalization, permissions)? |
| **Versions** | Can different replicas serve different versions (model, index, prompt, A/B test)? |
| **Capacity** | Is something overloaded (timeouts, rate limits, queue backlog, memory, GPU)? |
| **Dependencies** | Is a downstream service slow/failing (vector DB, LLM provider, DB)? |
| **Train/serve skew** | Is production computing something differently than training/evaluation did? |
| **Feedback loops** | Is the model influencing its own future training data? |

---

## Step 4 in detail — isolation techniques

| Technique | When to use |
|-----------|-------------|
| **Replay** the same input N times, log every intermediate output | Inconsistency, non-determinism |
| **Diff** a good request vs. bad request trace | "Works for some users, not others" |
| **Bisect** — freeze all layers except one | Any multi-layer pipeline |
| **Timeline correlation** — overlay metric drop with deploy/data events | Sudden degradation |
| **Slice** metrics by segment (region, device, user type, doc type, language) | "Accuracy dropped" |
| **Golden set** — fixed eval questions with known answers | Quality regressions |
| **Shadow / canary** — run new version alongside old | Before shipping a fix |

**Golden sentence for interviews:**
> "I'd find the *first layer where the output differs* between the good and bad case — that's where the bug lives."

---

## Step 5 — always give TWO fixes

Interviewers love this distinction:

- **Mitigation (stop the bleeding, minutes–hours):** rollback, feature flag off, fallback model, cache, rate limit, raise timeout, serve "I don't know".
- **Root-cause fix (days–weeks):** re-architecture, retraining, new pipeline, versioning, data contracts.

## Step 6 — prevention vocabulary

Use these words: **evals in CI**, **golden datasets**, **canary deploys**, **shadow traffic**, **drift monitoring**,
**SLOs + alerts**, **tracing (request ID through every layer)**, **data contracts / schema validation**,
**versioning (model, prompt, index, data)**, **runbooks**, **post-mortem**.

---

## Full worked example — the question you were asked

> **"Your RAG app has the same information, but gives different users different answers — and sometimes no answer at all. What do you do?"**

### Speak it like this (≈4 minutes)

**1. Clarify (30 sec)**
> "A few questions first. Is it the *exact same question text*, or similar questions? Different answers in wording, or in facts?
> Does the same user get different answers when they retry, or only different users? And 'no answer' — is that an 'I don't know',
> an error, or a timeout? Did anything change recently — model, prompt, documents?"

*(Interviewer will give you some answers. If they say "you decide", state your assumptions.)*

**2. Layer map (30 sec)** — draw the RAG pipeline above.

**3. Hypotheses, ranked (1 min)**

*Different answers to the same question:*
1. **Generation randomness** — temperature > 0, no seed. Most common cause.
2. **Per-user context** — chat history, user profile, or name/date injected into the prompt makes prompts differ.
3. **Permission / metadata filters** — users have different access rights (ACLs), so they retrieve different documents. *This may be correct behavior!*
4. **Retrieval non-determinism** — approximate nearest-neighbour search, ties in scores, different replica returns slightly different top-k, chunk order changes.
5. **Version skew** — replicas have different index versions (mid-reindex) or different model/prompt versions (A/B test, canary, provider silently updated model).
6. **Conflicting source docs** — two documents say different things (old policy vs new); whichever gets retrieved wins.
7. **Query rewriting** — an LLM rewrites the query non-deterministically, so retrieval differs.
8. **Caching** — some users hit a stale cached answer, others get a fresh one.

*Sometimes no answer:*
1. **Retrieval returns nothing above the similarity threshold** → model correctly says "I don't know" (threshold too strict, or query phrasing differs from document vocabulary).
2. **Context overflow / truncation** — long chat history pushes the retrieved chunks out of the token budget.
3. **Guardrail false positives** — input/output filters block legitimate answers.
4. **Timeouts / rate limits** from vector DB or LLM provider → app swallows the error and returns empty.
5. **Chunking bug** — the answer is split across chunks, or the doc failed to parse (PDF table, scanned image) and never got indexed.

**4. Isolate (1 min)**
> "I'd pick a few failing questions and **replay each one 20 times**, logging a full trace: rewritten query, retrieved chunk IDs and scores,
> final prompt hash, model version, and the answer.
> - If **chunk IDs differ** between runs → the problem is in retrieval (non-deterministic ANN, index version, query rewrite).
> - If **chunk IDs are the same but answers differ** → it's generation (temperature, prompt differences).
> - If **the prompt hashes differ** for different users → it's per-user context (history, profile, ACLs).
> - For 'no answer' cases I'd check: did retrieval return 0 chunks? Was there an error or timeout? Did a guardrail fire?"

**5. Fix (1 min)**

| Cause | Fix |
|-------|-----|
| Sampling | temperature = 0 (or low), fixed seed where supported, pin exact model version (`model-2025-xx-xx`, not `latest`) |
| Retrieval non-determinism | deterministic tie-break (sort by score, then doc_id); exact search for small corpora; hybrid search (BM25 + vectors) for stability |
| Version skew | **versioned indexes** + atomic alias swap (build new index fully, then flip pointer); pin model/prompt version per request and log it |
| Conflicting docs | dedupe, add `effective_date` / `source_of_truth` metadata, prefer latest, remove superseded docs |
| Per-user context | limit/ summarize history; keep volatile data (timestamp) out of prompt unless needed |
| ACLs | that's expected — but make the answer say "based on documents you have access to" |
| No retrieval hits | tune threshold on an eval set; query expansion / HyDE; hybrid search; better chunking |
| Overflow | token budgeting: reserve fixed space for retrieved context; summarize history |
| Errors | retries with backoff, fallback model, explicit error messages instead of empty answers |
| Cache | invalidate cache on index update (include index version in cache key) |

**6. Prevent (30 sec)**
> "I'd add a **consistency eval**: run each golden question 5–10 times and measure answer agreement — alert if below threshold.
> Add **retrieval metrics** (recall@k on a labeled set) and **groundedness** checks to CI. Log the model, prompt and index version on every request so
> any answer is reproducible. And monitor the rate of 'no answer' responses per day — a spike tells me retrieval or the provider broke."

**Why this answer wins:** it shows you know the full pipeline, you rank causes, you know how to *prove* the cause, and you think about production.

---

## Phrases that buy you thinking time (and sound senior)

- "Let me first make sure I understand the symptom…"
- "Let me walk through the request path, because every layer is a suspect."
- "The cheapest thing to check first is…"
- "I'd want to separate *retrieval* problems from *generation* problems."
- "This could actually be correct behavior if… — so I'd confirm the expected behavior first."
- "Short-term I'd mitigate by…, and the long-term fix is…"
- "To make sure this never happens silently again, I'd monitor…"
- "The trade-off here is… (latency vs quality / cost vs accuracy / freshness vs consistency)."

## What NOT to do

- ❌ Jump straight to "I'd fine-tune the model." (Most expensive fix, rarely the cause.)
- ❌ List 15 causes with no order. Rank them.
- ❌ Say "I'd check the logs" without saying **what** you'd look for in them.
- ❌ Forget the short-term mitigation. Production is burning *now*.
- ❌ Stay silent while thinking. Think out loud.
