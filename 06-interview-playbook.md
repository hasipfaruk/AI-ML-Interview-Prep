# 06. Interview Playbook & Cheat Sheet

## A. The 45-minute "Design X" script

| Time | Step | What you say / do |
|------|------|-------------------|
| 0-5 min | **Requirements** | "Let me clarify scope." Functional (3-5 features), non-functional (scale, latency, accuracy, cost, privacy). Write them down. Ask: *who are the users, how many, what matters most?* |
| 5-8 min | **Estimates** | QPS, storage, tokens/cost. Then **say what it means**: "So cost, not QPS, is the bottleneck." |
| 8-12 min | **API** | 3-5 endpoints. Mention streaming for LLMs. |
| 12-25 min | **High-level design** | Draw boxes & arrows. Walk one request end to end. For ML: show **offline** (data, training/ingestion) and **online** (serving) paths separately. |
| 25-38 min | **Deep dives** | Pick 2-3 hardest parts (or ask: "Which part would you like me to go deeper on?"). Data model, retrieval/ranking, scaling, evaluation. |
| 38-45 min | **What-ifs, trade-offs, monitoring** | Failure modes, bottlenecks, how you'd evaluate & monitor, what you'd do with more time. |

## B. The "What if X happens?" script
Use **C.L.H.I.F.P.** from [03-debugging-framework.md](03-debugging-framework.md):
1. **Clarify** the symptom (who / when / since when / what changed).
2. **Layer map**: draw the pipeline.
3. **Hypotheses** ranked by likelihood.
4. **Isolate**: cheapest test first; find the first layer where output differs.
5. **Fix**: mitigation now + root-cause fix later.
6. **Prevent**: evals, monitoring, alerts, versioning.

## C. What interviewers actually score
**Points in your favor:**
- You asked clarifying questions before designing.
- You stated assumptions out loud.
- You drove the conversation (didn't wait to be led).
- You explained **trade-offs** ("I chose X over Y because…, the cost is…").
- You covered evaluation and monitoring (very important for ML roles).
- You started simple, then scaled ("for v1 I'd use pgvector; at 100M vectors I'd move to…").
- You handled pushback calmly ("Good point. In that case I'd change…").

**Points against you:**
- Jumping into a model architecture before understanding the problem.
- Listing buzzwords without reasons.
- Long silences.
- Over-engineering a system that only gets 5 QPS.
- Ignoring the cost and latency of LLM calls.

## D. Trade-off sentences (memorize the shape)
- "**X gives us** lower latency, **at the cost of** staleness, **which is acceptable here because** …"
- Latency vs quality: bigger model / reranker / more context = better but slower and costlier.
- Freshness vs cost: real-time ingestion vs hourly batch.
- Consistency vs availability: payments → consistency; feeds → availability.
- Precision vs recall: depends on the cost of each error type.
- Build vs buy: managed vector DB/LLM API (speed) vs self-host (control, cost at scale).
- RAG vs fine-tune: knowledge vs behavior.
- Determinism vs creativity: temperature 0 for factual Q&A, higher for brainstorming.

## E. One-page cheat sheet

**Building blocks:** LB · API gateway · cache (Redis) · CDN · SQL · NoSQL · object storage · queue (SQS/Rabbit) · stream (Kafka) · search (Elastic) · vector DB · feature store · model registry · model server · LLM gateway · monitoring/tracing.

**Scale moves:** stateless + horizontal · cache · read replicas · shard · async queue · CDN · batch on GPU · autoscale · multi-region.

**Reliability moves:** redundancy · timeouts · retries with backoff + jitter · circuit breaker · fallback/degradation · idempotency · canary + rollback · rate limits · DLQ.

**ML moves:** feature store (no skew) · point-in-time joins · time-based splits · shadow → canary → A/B · drift monitoring · champion/challenger · version code+data+model.

**LLM/RAG moves:** hybrid search · rerank · good chunking + contextual headers · query rewrite · ACL pre-filter · citations · "I don't know" threshold · temp 0 + pinned model for consistency · versioned index + alias swap · semantic/prompt cache · model routing · streaming · token budgets · guardrails · evals in CI (recall@k, faithfulness, consistency).

**Numbers:** 1M/day ≈ 12 QPS · 1 day ≈ 10⁵ s · 1 token ≈ 4 chars · 1536-d fp32 vector ≈ 6 KB · 7B fp16 ≈ 14 GB · Redis ~1 ms · LLM TTFT ~0.5 s · 99.9% = 8.8 h/yr down.

## F. Common questions to prepare answers for
1. Design a RAG system for internal documents. *(05 #1)*
2. Design a chatbot/agent for customer support. *(05 #2)*
3. How would you evaluate an LLM application? *(02 §10)*
4. How do you reduce hallucinations? *(04 #3)*
5. RAG vs fine-tuning: when to use each? *(02 §12)*
6. How do you reduce LLM latency / cost? *(04 #6, #11, 02 §8)*
7. Design a recommendation system. *(05 #4)*
8. Design fraud detection. *(05 #5)*
9. Model works offline but not in production. Why? *(04 #23)*
10. How do you detect and handle drift? *(04 #24)*
11. How do you deploy a new model safely? *(02 §5, 04 #43)*
12. Same question, different answers. Why? *(03 worked example)*
13. How to handle multi-tenant data isolation? *(04 #7)*
14. How to serve a 70B model? *(02 §8, 04 #41)*
15. How do you defend against prompt injection? *(04 #15)*

## G. Your 2-week mock interview plan
| Day | Task |
|-----|------|
| 1, 3, 5, 7, 9, 11, 13 | One full 45-min design (rotate 05 cases), **recorded**. Watch back: Did I clarify? Estimate? Trade-offs? Monitoring? |
| 2, 4, 6, 8, 10, 12, 14 | 8 scenario questions from 04, 3 min each, out loud, timed |
| Daily | 10 min: redraw the RAG layer map and ML lifecycle from memory |

**Practice partners:** a friend, a peer engineer, or ask an AI to play interviewer: *"Act as a senior ML interviewer. Ask me a system design question, then push back with 'what if' failure scenarios. Score me on structure, trade-offs, and depth."*

## H. If you blank out in the interview
Say: *"Let me take a step back and walk through the request path."* Then draw the pipeline. Your layer map will give you the next thing to say.
