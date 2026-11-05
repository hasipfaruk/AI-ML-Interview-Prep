# 01 — System Design Fundamentals (Zero → Solid)

Even ML/AI interviews expect these basics. Every AI system is still a web system underneath.

### Contents
1. [The big picture](#part-1--the-big-picture)
2. [Networking & APIs](#part-2--networking--apis)
3. [Scaling: load balancers, caching, CDN](#part-3--scaling-load-balancers-caching-cdn)
4. [Databases](#part-4--databases)
5. [Async processing: queues & streams](#part-5--async-processing-queues--streams)
6. [Distributed systems concepts](#part-6--distributed-systems-concepts)
7. [Reliability, monitoring, security](#part-7--reliability-monitoring-security)
8. [Back-of-the-envelope estimation](#part-8--back-of-the-envelope-estimation)

---

## Part 1 — The big picture

**System design = deciding which components you need and how they talk, so the system meets its requirements at scale.**

Two kinds of requirements:
- **Functional** — what it does ("users can upload documents and ask questions").
- **Non-functional** — how well: scale, latency, availability, consistency, cost, security.

### The growth story (memorize this — it's the skeleton of every design)
```
Stage 1:  User → [Single server: app + DB]                      (works for ~100s of users)
Stage 2:  User → [App server] → [Database]                      (separate concerns)
Stage 3:  User → [Load balancer] → [App 1..N] → [Database]      (horizontal scaling)
Stage 4:  ... + [Cache] in front of DB                          (fast reads)
Stage 5:  ... + [CDN] for static files                          (global speed)
Stage 6:  ... + DB replicas (reads) + sharding (writes)         (data scale)
Stage 7:  ... + [Queue] → [Workers] for slow jobs               (async)
Stage 8:  ... + multiple regions, monitoring, autoscaling       (global + reliable)
```

### The 5 qualities you trade off
| Quality | Question | Typical tool |
|---------|----------|--------------|
| Scalability | Handle 10× users? | horizontal scaling, sharding, queues |
| Latency | How fast? | caching, CDN, indexes, async |
| Availability | Stays up when parts fail? | replication, redundancy, failover |
| Consistency | Everyone sees the same correct data? | single leader, transactions, quorum |
| Cost | Affordable? | right-sizing, caching, batch vs real-time |

---

## Part 2 — Networking & APIs

**What happens when you type a URL:** DNS resolves name → IP → TCP connection (+ TLS handshake for HTTPS) → HTTP request → load balancer → server → response.

| Concept | One-liner |
|---------|-----------|
| **IP / DNS** | IP = address of a machine; DNS = phone book from name to IP |
| **TCP** | Reliable, ordered delivery (web, APIs, DBs) |
| **UDP** | Fast, no guarantees (video calls, gaming, DNS) |
| **HTTP/HTTPS** | Request/response protocol; HTTPS = encrypted via TLS |
| **HTTP/2, HTTP/3** | Multiplexing many requests on one connection; HTTP/3 over QUIC (UDP) |

### API styles
| Style | Use when | Example |
|-------|----------|---------|
| **REST** | Default for public/CRUD APIs | `GET /documents/42` |
| **GraphQL** | Clients need flexible queries, many entity types | mobile apps |
| **gRPC** | Fast internal service-to-service calls (binary, typed) | model server calls |
| **WebSocket** | Two-way real-time | chat, live collaboration |
| **SSE (server-sent events)** | Server → client streaming | **streaming LLM tokens** |
| **Long polling** | Simple near-real-time fallback | notifications |
| **Webhooks** | Notify another system when something happens | "payment completed" |

### Good API design rules
- Nouns for resources, HTTP verbs for actions (`POST /chats/{id}/messages`).
- **Pagination** (cursor-based for large lists), **versioning** (`/v1/`), **idempotency keys** for POST that must not run twice (payments), proper status codes (200, 201, 400, 401, 403, 404, 429, 500, 503).
- **Rate limiting** per user/API key.

---

## Part 3 — Scaling: load balancers, caching, CDN

### Vertical vs horizontal scaling
- **Vertical** = bigger machine. Simple, but has a ceiling and is a single point of failure.
- **Horizontal** = more machines. Needs **stateless** servers (sessions in Redis/DB, not memory).

### Load balancer
Spreads requests across servers, removes unhealthy ones (health checks).
- **L4** (TCP level, fast) vs **L7** (HTTP level — can route by URL/header, e.g., `/api/llm` → GPU pool).
- Algorithms: round-robin, least connections, weighted, consistent hashing (sticky by key).
- Related: **reverse proxy** (Nginx), **API gateway** (auth, rate limiting, routing, logging in one place).

### Caching
Store results of expensive operations in fast memory (Redis/Memcached).

| Pattern | How it works | Use |
|---------|--------------|-----|
| **Cache-aside** (most common) | App checks cache → miss → read DB → write cache | general reads |
| **Write-through** | Write to cache and DB together | data read right after write |
| **Write-back** | Write to cache, flush to DB later | high write rate, risk of loss |
| **TTL** | Entries expire after time | everything |

- **Eviction:** LRU (least recently used) is the default answer.
- **Problems you should mention:**
  - *Stale data* → TTL + invalidate on write.
  - *Thundering herd / cache stampede* → many requests miss at once and hit DB → use locks / request coalescing / staggered TTLs.
  - *Hot key* → one key gets huge traffic → replicate key, local cache.
- **AI-specific:** exact-match cache for prompts, **semantic cache** (embed query, return cached answer if similarity > threshold), embedding cache, **KV/prefix cache** in LLM servers.

### CDN
Copies static files (images, JS, videos, model files) to servers worldwide. Users download from nearest location.

### Rate limiting algorithms
- **Token bucket** (most common): bucket refills at rate R, each request takes a token; allows bursts.
- **Leaky bucket**: smooth constant output.
- **Fixed window / sliding window counter**: count requests per time window.
- Store counters in Redis for distributed limits. For LLMs, limit **tokens per minute**, not just requests.

---

## Part 4 — Databases

### SQL vs NoSQL
| | SQL (Postgres, MySQL) | NoSQL |
|---|---|---|
| Model | Tables, relations, joins | Key-value (Redis, DynamoDB), document (MongoDB), wide-column (Cassandra), graph (Neo4j) |
| Strength | Transactions (ACID), complex queries, correctness | Massive scale, flexible schema, high write throughput |
| Pick when | Payments, users, orders, metadata | Chat messages, event logs, sessions, feeds |

**Interview default:** "I'll start with Postgres for metadata because we need consistency and joins; I'd move high-volume append-only data like chat messages to Cassandra/DynamoDB."

**Specialized stores you should name:**
- **Object storage** (S3/GCS): files, images, model weights, datasets — cheap, huge.
- **Vector DB** (Pinecone, Weaviate, Milvus, Qdrant, pgvector): embeddings + similarity search.
- **Search engine** (Elasticsearch/OpenSearch): full-text keyword search, inverted index, BM25.
- **Data warehouse / lakehouse** (BigQuery, Snowflake, Databricks): analytics, training data.
- **Time-series DB**: metrics. **Feature store** (Feast, Tecton): ML features.

### ACID vs BASE
- **ACID** — Atomic, Consistent, Isolated, Durable (bank transfers).
- **BASE** — Basically Available, Soft state, Eventually consistent (likes counter).

### Indexes
Like a book index — makes reads fast, writes slightly slower. B-tree (most SQL), LSM-tree (write-heavy: Cassandra, RocksDB). For vectors: **HNSW** (graph, fast, memory-heavy), **IVF** (clusters), **PQ** (compression).

### Replication
Copies of data on multiple machines.
- **Leader-follower:** writes go to leader, reads from followers. Followers may lag → **replication lag** (user writes, then reads old data). Fix: read-your-own-writes from leader.
- **Multi-leader:** writes in multiple regions; must resolve conflicts.
- **Leaderless (quorum):** write to W nodes, read from R nodes; if **W + R > N** you read latest data.

### Sharding (partitioning)
Split data across machines.
- **By hash of key** (even spread) — `shard = hash(user_id) % N`.
- **By range** (good for range queries, risk of hot spots).
- **By tenant** (common in B2B/RAG — isolation per customer).
- **Consistent hashing:** keys and servers on a ring; adding a server only moves ~1/N keys. (Used in caches, Cassandra, DynamoDB.)
- Problems: hot shards, cross-shard joins, resharding.

### Denormalization
Duplicate data to avoid joins for fast reads (e.g., store author name inside post). Trade-off: harder updates.

---

## Part 5 — Async processing: queues & streams

**Why:** don't make users wait for slow work (embedding a 500-page PDF, sending emails, training jobs).
```
API → [Queue] → Workers (scale independently) → result in DB → notify user (webhook / polling / websocket)
```
| Tool | Type | Use |
|------|------|-----|
| RabbitMQ / SQS | Message queue (task consumed once) | background jobs |
| Kafka / Kinesis / Pub/Sub | Log/stream (many consumers, replayable) | event streaming, feature pipelines, logs |

- **Delivery guarantees:** at-most-once, **at-least-once (default)**, exactly-once (hard). With at-least-once, make consumers **idempotent**.
- **Dead-letter queue (DLQ):** messages that fail repeatedly go aside for inspection.
- **Backpressure:** when consumers can't keep up — queue grows; autoscale workers or slow producers.
- **Batch vs stream processing:** Spark (batch, hourly/daily) vs Flink/Kafka Streams (real-time). ML: batch features vs real-time features.

### Architecture styles
- **Monolith** — one deployable. Start here. Simple.
- **Microservices** — separate services per domain; independent scaling & deploys; cost: network calls, distributed debugging.
- **Event-driven** — services react to events on Kafka.
- **CQRS** — separate write model and read model.
- **Saga** — distributed transaction as a sequence of local steps with compensating actions.

---

## Part 6 — Distributed systems concepts

| Concept | Plain explanation |
|---------|------------------|
| **CAP theorem** | During a network **P**artition you must choose **C**onsistency (reject requests) or **A**vailability (serve possibly stale data). Payments → CP. Social feed → AP. |
| **PACELC** | Even without partition: trade-off between **L**atency and **C**onsistency. |
| **Eventual consistency** | All replicas converge eventually; reads may be stale briefly. |
| **Strong consistency** | Every read sees latest write. Slower. |
| **Consensus (Raft/Paxos)** | Nodes agree on a value/leader despite failures (etcd, ZooKeeper). |
| **Leader election** | Pick one node to coordinate (e.g., one scheduler for training jobs). |
| **Idempotency** | Doing an operation twice = same result as once. Essential with retries. |
| **Retries + exponential backoff + jitter** | Retry after 1s, 2s, 4s (+ random) to avoid overwhelming a recovering service. |
| **Circuit breaker** | Stop calling a failing service for a while; return fallback. |
| **Bulkhead** | Isolate resources so one failure doesn't sink everything (separate pools). |
| **Timeouts** | Every network call needs one. |
| **Unique IDs** | UUID (random), Snowflake (time + machine + sequence, sortable). |
| **Bloom filter** | Tiny structure answering "definitely not in set / maybe in set" (crawler seen-URLs). |
| **Heartbeats / gossip** | Detect dead nodes / spread cluster state. |
| **2PC** | Two-phase commit across DBs — consistent but slow and blocking. |

---

## Part 7 — Reliability, monitoring, security

### Availability numbers
| Availability | Downtime/year |
|--------------|---------------|
| 99% | 3.65 days |
| 99.9% | 8.8 hours |
| 99.99% | 52 minutes |
| 99.999% | 5 minutes |

- **No single point of failure:** redundancy everywhere (multiple servers, replicas, zones).
- **Failover:** active-passive or active-active.
- **SLI / SLO / SLA:** indicator (p95 latency), objective (p95 < 2s for 99% of days), agreement (contract with penalties).

### Observability (3 pillars)
- **Metrics** — numbers over time (QPS, latency p50/p95/p99, error rate, GPU utilization, token usage).
- **Logs** — events with details.
- **Traces** — one request followed across all services (OpenTelemetry). **For LLM apps: trace every step — retrieval, prompt, model call, tokens, cost.**

### Deployments
- **Blue-green:** two environments, switch traffic.
- **Canary:** send 1–5% of traffic to new version, watch metrics, then expand.
- **Shadow:** new version receives copy of traffic, its outputs are not shown to users (great for ML models).
- **Feature flags:** turn features on/off without deploy.

### Security basics
- **AuthN** (who are you: OAuth2/OIDC, JWT) vs **AuthZ** (what can you do: RBAC/ABAC).
- Encryption in transit (TLS) and at rest.
- Secrets in a vault, never in code/prompts.
- Least privilege, audit logs, input validation, multi-tenant isolation.

---

## Part 8 — Back-of-the-envelope estimation

### Numbers to memorize
| | |
|---|---|
| 1 day | ≈ 86,400 s ≈ **10⁵ s** |
| 1M requests/day | ≈ **12 QPS** |
| 100M requests/day | ≈ 1,200 QPS |
| Peak traffic | ≈ 2–3× average |
| Memory read | ~100 ns |
| SSD read | ~100 µs |
| Same-datacenter network round trip | ~0.5 ms |
| Cross-continent round trip | ~150 ms |
| Redis get | ~1 ms |
| DB indexed query | ~5–50 ms |
| LLM first token | ~200–800 ms |
| LLM generation | ~30–100 tokens/s per stream |
| 1 token | ≈ 0.75 English words ≈ 4 chars |
| Embedding (float32, 1536 dims) | 1536 × 4 B ≈ **6 KB** |
| 7B model in FP16 | ≈ 14 GB GPU memory (2 bytes/param) |

### Formula
```
QPS          = daily_requests / 86,400          (× 2–3 for peak)
Storage      = items × size × retention
Bandwidth    = QPS × response_size
Servers      = peak QPS / QPS_per_server
```

### Worked example — RAG for a company with 10,000 employees
- Each asks 10 questions/day → 100k/day → **~1.2 QPS avg, ~5 QPS peak**. (Small! Don't over-engineer.)
- Corpus: 1M documents × 10 chunks = **10M chunks** × 6 KB = **60 GB vectors** (+ HNSW overhead ~1.5×) → fits on one vector DB node with replicas; or compress with PQ.
- LLM tokens: 100k × (3k input + 300 output) = 330M tokens/day → cost estimate from price per million tokens.
- Conclusion: the bottleneck is **LLM cost and latency**, not QPS → focus on caching, routing, context size.

> **Interview tip:** Always say what the numbers *mean* for the design ("5 QPS means a single service with 2 replicas for HA is enough; the real concern is cost").
