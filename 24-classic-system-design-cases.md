# 24. Classic System Design Cases (For Any Engineer)

These are the classic "design X" questions asked in backend, full-stack, platform and ML engineer interviews.
Basics (load balancers, caching, sharding, queues) are in [01-fundamentals.md](01-fundamentals.md). URL shortener, chat app and rate limiter are in [05-case-studies.md](05-case-studies.md#9-url-shortener).

Every case uses the same 7 steps:
> **1. Requirements → 2. Estimates → 3. API → 4. High-level design → 5. Data model → 6. Deep dives → 7. What-ifs & trade-offs**

### Contents
1. [News feed (social network)](#1-news-feed-social-network)
2. [Video streaming platform](#2-video-streaming-platform)
3. [Ride-hailing (geo-indexing)](#3-ride-hailing-geo-indexing)
4. [Collaborative document editing](#4-collaborative-document-editing)
5. [File sync and storage](#5-file-sync-and-storage)
6. [Payment system](#6-payment-system)
7. [Notification system](#7-notification-system)
8. [Web crawler](#8-web-crawler)
9. [Search autocomplete (typeahead)](#9-search-autocomplete-typeahead)
10. [Distributed key-value store](#10-distributed-key-value-store)
11. [Distributed message queue](#11-distributed-message-queue)
12. [Ticket booking (seat locking)](#12-ticket-booking-seat-locking)
13. [Hotel / home rental booking](#13-hotel--home-rental-booking)
14. [Metrics & monitoring system](#14-metrics--monitoring-system)
15. [Distributed job scheduler](#15-distributed-job-scheduler)
16. [Real-time leaderboard](#16-real-time-leaderboard)
17. [Proximity search (nearby places)](#17-proximity-search-nearby-places)
18. [Stock exchange / order matching](#18-stock-exchange--order-matching)
19. [Email service](#19-email-service)
20. [CDN design](#20-cdn-design)
21. [Patterns that repeat across cases](#21-patterns-that-repeat-across-cases)

---

## 1. News feed (social network)
> "Design the home timeline of a social network like Twitter/X."

**1. Requirements**
- Functional: post (text + media), follow users, see a home feed of people you follow (newest or ranked), like/reply.
- Non-functional: feed loads < 200 ms, highly available (stale by a few seconds is OK), read-heavy (~100 reads per write).

**2. Estimates:** 300M DAU, each opens feed 10×/day → 3B reads/day ≈ 35k QPS (peak ~100k). Posts: 300M × 0.5 = 150M/day ≈ 1.7k writes/s. Post metadata 1 KB → 150 GB/day.

**3. API**
```
POST /v1/posts                 { text, media_ids }
GET  /v1/feed?cursor=...       → list of posts (cursor pagination)
POST /v1/users/{id}/follow
```

**4. High-level design**
```
Client → LB → Post service → Posts DB (sharded by post_id) + Media → object storage/CDN
                   │
                   └─► Queue → Fan-out workers ──► Feed cache (Redis: user_id → list of post_ids)
Client → LB → Feed service → read Feed cache → hydrate posts (Post cache) → (ranking) → client
Follow service → Social graph DB (followers / following)
```

**5. Data model:** `posts(post_id, author_id, text, media, created_at)`, `follows(follower_id, followee_id)`, feed cache: `feed:{user_id} → [post_id, ...]` (keep last ~800).

**6. Deep dives**
- **Fan-out on write (push):** when a user posts, write the post_id into every follower's feed cache. Fast reads, slow writes.
- **Fan-out on read (pull):** at read time, fetch recent posts from everyone you follow and merge. Slow reads, cheap writes.
- **Hybrid (the usual answer):** push for normal users; for **celebrities** (millions of followers) don't fan out. Merge their posts at read time instead.
- Ranking: candidate posts → ranking model (see [05 #4](05-case-studies.md#4-recommendation-system)).
- IDs: time-sortable Snowflake IDs so feeds sort by ID.

**7. What-ifs & trade-offs**
- *Celebrity posts → fan-out storm:* hybrid model above; rate-limit fan-out workers.
- *Feed cache lost (Redis failure):* rebuild lazily from Posts DB via pull model; replicas for cache.
- *User sees deleted post:* soft delete flag checked at hydration time.
- Trade-off: freshness vs cost. A fan-out lag of a few seconds is acceptable.

---

## 2. Video streaming platform
> "Design a video platform like YouTube: upload and watch videos."

**1. Requirements:** upload, transcode, watch on any device/network, search, view counts. Smooth playback, global, very read-heavy.

**2. Estimates:** 500 hours of video uploaded per minute. 1B views/day ≈ 12k QPS for video starts. Storage huge: each video stored in many resolutions (~5× original). Bandwidth is the biggest cost → **you need a CDN**.

**3. API**
```
POST /v1/videos/upload-url     → pre-signed URL for direct upload to object storage
POST /v1/videos                { title, description, upload_id }
GET  /v1/videos/{id}           → metadata + manifest URL
```

**4. High-level design**
```
Upload:  Client ──(pre-signed URL)──► Object storage (raw)
                    │ event
                    ▼
              Queue → Transcoding workers (split into chunks, encode in parallel:
                      240p…4K, codecs H.264/VP9/AV1) → Object storage (segments + HLS/DASH manifest)
                    → Thumbnails, content moderation, captions (ML)
                    → Metadata DB status = READY → CDN pre-warm for popular channels
Watch:   Client → API → metadata DB/cache → manifest URL
         Client player ──► CDN edge (segments) ──miss──► origin storage
```

**5. Data model:** `videos(video_id, owner_id, title, status, duration, created_at)`, `video_files(video_id, resolution, codec, path)`, view counts in a separate counter store.

**6. Deep dives**
- **Adaptive bitrate streaming (HLS/DASH):** video cut into 2-10 s segments at multiple bitrates; player switches quality based on bandwidth.
- **Parallel transcoding:** split video into chunks → DAG of tasks → merge. Resumable uploads (chunked upload).
- **View counts:** don't write to DB per view; count in stream (Kafka) → aggregate → batch update. Approximate is OK.
- **Cost:** popular videos on CDN; long-tail videos served from fewer locations / cheaper storage tier.

**7. What-ifs:** *Transcoding backlog:* autoscale workers, prioritize by channel popularity. *Viral video overloads origin:* CDN request coalescing, pre-warm. *Upload fails at 90%:* resumable chunked uploads. *Copyrighted content:* fingerprinting at upload.

---

## 3. Ride-hailing (geo-indexing)
> "Design a ride-hailing app like Uber."

**1. Requirements:** rider requests ride, match with nearby driver, live driver location, trip tracking, pricing, payment. Matching < few seconds, location updates every ~4 s.

**2. Estimates:** 5M active drivers sending location every 4 s → **~1.25M location writes/s** (this is the hard part). Ride requests: ~1k/s.

**3. API**
```
POST /v1/drivers/location      { lat, lng }   (or via WebSocket)
POST /v1/rides                 { pickup, dropoff } → ride_id
GET  /v1/rides/{id}            → status, driver location
```

**4. High-level design**
```
Driver app ──WebSocket──► Location service ──► Geo index (in-memory, Redis GEO / custom grid)
                                    └──► Kafka (location stream → analytics, ETA models, trip history)
Rider app → Ride service → Matching service: query geo index for nearby available drivers
                         → rank by ETA → send offer to driver (timeout → next driver)
                         → Trip service (state machine) → Payment service
Pricing service (surge = demand/supply per area)   ETA service (routing graph + ML)
```

**5. Data model:** `drivers(driver_id, status, vehicle)`, live location only in memory (`geo cell → set of driver_ids`), `trips(trip_id, rider_id, driver_id, state, route, fare)`.

**6. Deep dives**
- **Geo-indexing:** split the map into cells: **geohash** (string prefix = area), **quadtree** (split dense areas more), or **H3 hexagons** (equal-size neighbours). Query: my cell + neighbour cells.
- Location data is **ephemeral**. Keep it in memory, sharded by region/city; don't write every update to a DB.
- **Matching consistency:** a driver must not get two rides → lock driver (atomic status change `AVAILABLE → OFFERED` with compare-and-set).
- Trip as a **state machine**: requested → matched → arriving → in_progress → completed → paid.

**7. What-ifs:** *Driver app loses network:* mark stale after N missed heartbeats. *Geo index node crashes:* rebuild in seconds from next location updates. *Hotspot (concert ends):* smaller cells in dense areas, surge pricing. *Two riders matched to same driver:* atomic CAS on driver status.

---

## 4. Collaborative document editing
> "Design a real-time collaborative editor like Google Docs."

**1. Requirements:** many users edit the same doc at once, see each other's changes and cursors in < 100 ms, offline edits, version history, permissions.

**2. Estimates:** most docs have 1-5 concurrent editors; few have 100+. Edit operations small (few bytes) but frequent.

**3. API:** `GET /docs/{id}` (snapshot + version), WebSocket `/docs/{id}/session` for sending/receiving operations.

**4. High-level design**
```
Clients ──WebSocket──► Collaboration servers (one "owner" server per document, chosen by consistent hashing)
                          │  apply OT/CRDT, assign order, broadcast to other clients
                          ├─► Operation log (append-only, per doc)
                          └─► Periodic snapshots → Document store
Presence (cursors) via the same socket, not persisted.
```

**5. Data model:** `documents(doc_id, owner, acl)`, `operations(doc_id, version, op, user_id, ts)`, `snapshots(doc_id, version, content)`.

**6. Deep dives**
- **The core problem:** two users edit the same place at the same time. Need all copies to end up identical.
- **OT (Operational Transformation):** a central server orders operations and *transforms* each incoming op against concurrent ones (e.g., shift an insert position). Used by Google Docs. Needs a central server.
- **CRDT (Conflict-free Replicated Data Types):** each character has a unique ID and position; merges are automatic and order-independent. Works peer-to-peer and offline. More memory. Used by Figma-style/local-first apps (Yjs, Automerge).
- Version history = snapshots + op log replay.

**7. What-ifs:** *User offline for an hour:* queue ops locally, rebase/merge on reconnect (CRDT easier). *Owner server dies:* another server takes the doc, rebuilds from snapshot + log. *Huge doc slow to load:* snapshot + lazy loading.

---

## 5. File sync and storage
> "Design a file sync service like Dropbox / Google Drive."

**1. Requirements:** upload/download, sync across devices, share, version history, works with large files and bad networks.

**2. Estimates:** 50M users × 10 GB = 500 PB. Most files rarely change.

**3. API:** `POST /files/chunks/check {hashes}` → which chunks are missing; `PUT /chunks/{hash}`; `POST /files/commit {path, chunk_list, base_version}`; long-poll/WebSocket `/changes?cursor=`.

**4. High-level design**
```
Client (watcher + chunker) ──► Metadata service ──► Metadata DB (files, versions, chunk lists), strongly consistent
                          ──► Block service ──► Object storage (chunks addressed by hash)
Notification service ──► other devices pull changes
```

**5. Data model:** `files(file_id, owner, path, latest_version)`, `versions(file_id, version, chunk_hashes[], modified_by)`, `chunks(hash, size, location, ref_count)`.

**6. Deep dives**
- **Chunking (4 MB) + content hashing:** only upload changed chunks (delta sync), resumable, **deduplication** (same chunk stored once across users).
- Metadata needs **strong consistency** (SQL); blocks need durability (object storage, replicated).
- **Conflicts:** two devices edit offline → commit with `base_version`; if stale, keep both ("conflicted copy").

**7. What-ifs:** *Huge file on mobile network:* chunked, resumable, pause on metered networks. *Ransomware encrypts files and syncs:* version history + bulk-restore. *Deleting a deduplicated chunk:* reference counting + delayed garbage collection.

---

## 6. Payment system
> "Design a payment system for an e-commerce site."

**1. Requirements:** charge customers via card/wallet (external payment providers), refunds, pay out sellers, never lose or double-charge money, audit trail.

**2. Estimates:** 1M orders/day ≈ 12 TPS. Throughput is small. **Correctness is what matters.**

**3. API**
```
POST /v1/payments   { order_id, amount, currency, method }   Header: Idempotency-Key
GET  /v1/payments/{id}
POST /v1/refunds    { payment_id, amount }                    Header: Idempotency-Key
Webhook from provider: /v1/provider-events
```

**4. High-level design**
```
Checkout → Payment service ──► Payments DB (state machine)  ──► Payment provider (card network)
                │                        ▲                              │
                │                        └──── webhook / poll status ◄──┘
                └──► Ledger service (double-entry, append-only)
                └──► Outbox → Kafka → order service, notifications, payouts
Nightly reconciliation job: our ledger vs provider settlement files → mismatches → alerts / manual review
```

**5. Data model:** `payments(payment_id, order_id, idempotency_key UNIQUE, amount, currency, status, provider_ref)`, `ledger_entries(entry_id, txn_id, account_id, debit, credit, created_at)`. Every transaction has entries whose debits = credits.

**6. Deep dives**
- **Idempotency:** client sends a unique key; server stores it with the result; a retry returns the stored result instead of charging again.
- **State machine:** created → pending → succeeded / failed → refunded. Only valid transitions allowed.
- **Double-entry ledger:** money moves between accounts (customer → platform → seller); append-only, never update. Easy auditing.
- **Unknown outcome** (timeout from provider): mark *pending*, query provider status / wait for the webhook. Never blindly retry with a new key.
- **Exactly-once effects** via idempotency + **transactional outbox** (write event in the same DB transaction).
- Money as integers (cents) + currency, never floats. PCI: don't store card numbers. Use provider tokens.

**7. What-ifs:** *Provider timed out, did the charge happen?* → pending + reconcile. *Webhook arrives twice:* dedupe by event ID. *Ledger and provider disagree:* reconciliation flags it, human review. *Provider down:* failover to second provider for new payments.

---

## 7. Notification system
> "Design a system that sends push, SMS and email notifications."

**1. Requirements:** many services send notifications; channels push/SMS/email/in-app; user preferences & opt-out; templates; scheduling; rate limits; no spam/duplicates.

**2. Estimates:** 10M push + 1M SMS + 5M email per day; spikes during campaigns.

**3. API:** `POST /v1/notifications { user_id, template_id, params, channels, priority, dedupe_key }`.

**4. High-level design**
```
Services → Notification API → validate, check preferences & rate limits, render template
        → Priority queues per channel (Kafka/SQS: high = OTP, low = marketing)
        → Channel workers → providers (APNs/FCM, SMS gateway, email provider)
        → Delivery status / retries / DLQ → status DB → analytics
```

**6. Deep dives:** separate queues so marketing floods don't delay OTP codes; retries with backoff; dedupe by `dedupe_key`; user quiet hours & time zones; provider failover; tracking (delivered, opened).

**7. What-ifs:** *Campaign of 50M emails slows OTPs:* priority queues. *Provider down:* failover provider. *User receives same notification 3×:* idempotent workers + dedupe key. *Device tokens expired:* remove on provider feedback.

---

## 8. Web crawler
> "Design a crawler that downloads 1 billion pages per month."

**1. Requirements:** crawl the web, respect robots.txt and politeness, avoid duplicates, refresh pages, store content for indexing.

**2. Estimates:** 1B pages / month ≈ 400 pages/s; 500 KB/page → 500 TB/month.

**4. High-level design**
```
Seed URLs → URL frontier (priority + per-host queues for politeness)
          → Fetchers (DNS cache, robots.txt cache) → content
          → Dedupe (content hash / SimHash for near-duplicates) → Object storage
          → Parser → extract links → URL filter (seen? Bloom filter) → back to frontier
```

**6. Deep dives:** **politeness:** one queue per host, delay between requests; **URL seen check** with Bloom filter + DB; **priority** by PageRank/freshness; **recrawl** frequency by change rate; distributed by hashing host → crawler node.

**7. What-ifs:** *Crawler trap (infinite calendar URLs):* max depth, URL pattern limits. *Site blocks us:* slow down, respect robots. *Duplicate content on many URLs:* canonical URLs + SimHash.

---

## 9. Search autocomplete (typeahead)
> "Show top 5 suggestions as the user types."

**1. Requirements:** suggestions in < 100 ms per keystroke, ranked by popularity (+ personalization), updated daily or near-real-time, filter offensive terms.

**2. Estimates:** 10M DAU × 20 searches × 6 keystrokes = 1.2B requests/day ≈ 14k QPS.

**4. High-level design**
```
Offline: search logs → aggregate counts (Spark, daily) → build Trie with top-k precomputed at each node → snapshot
Online:  Client (debounce 100 ms, browser cache) → CDN/edge cache → Autocomplete service (trie in memory, sharded by prefix) 
```

**6. Deep dives:** store **top-k at each trie node** (no traversal at query time); shard by first letters (watch for skew); real-time trending via stream counts merged with daily trie; personalization re-ranks a few results.

**7. What-ifs:** *Breaking news term missing:* streaming trending layer. *Offensive suggestion:* blocklist filter before serving. *Hot prefix "a" overloads shard:* cache common prefixes at edge.

---

## 10. Distributed key-value store
> "Design a key-value store like DynamoDB/Cassandra."

**1. Requirements:** `put(key, value)`, `get(key)`; huge scale; highly available; tunable consistency.

**4. Design (key ideas)**
```
Client → any node (coordinator) → consistent hashing ring → N replicas (e.g., N=3)
Write path: commit log (WAL) → memtable (memory) → flush to SSTables on disk → compaction
```
- **Partitioning:** consistent hashing with **virtual nodes** (even load, easy scaling).
- **Replication:** N copies on next nodes of the ring, across zones.
- **Quorum:** write to W, read from R; **W + R > N** → strong-ish consistency. Lower W/R → faster, more available.
- **Conflicts:** last-write-wins (timestamps) or vector clocks (detect concurrent writes).
- **Failure handling:** **hinted handoff** (another node holds writes for a dead node), **read repair**, **anti-entropy with Merkle trees**, gossip for membership.
- Storage: an **LSM tree** for fast writes; Bloom filters to skip SSTables on reads.

**7. What-ifs:** *Node dies:* hinted handoff, then replace and stream data. *Network partition:* choose AP (accept writes, resolve later) or CP (reject) per CAP. *Hot key:* add caching / key splitting.

---

## 11. Distributed message queue
> "Design a message queue / log like Kafka."

**Key ideas**
```
Producers → Broker cluster: topic split into partitions (append-only log on disk)
            each partition: 1 leader + followers (replication, ISR = in-sync replicas)
Consumers in a consumer group: each partition read by one consumer in the group; consumer tracks offset
Controller (Raft/ZooKeeper) handles leader election and metadata
```
- **Ordering** guaranteed only within a partition → choose partition key (e.g., user_id) for per-entity order.
- **Durability:** `acks=all` waits for all in-sync replicas.
- **Retention** by time/size; consumers can **replay** from an offset.
- **Throughput:** sequential disk writes, batching, compression, zero-copy.
- **Delivery semantics:** at-least-once by default (commit offset after processing) → idempotent consumers; exactly-once via idempotent producers + transactions.

**What-ifs:** *Consumer lag grows:* add partitions + consumers, speed up processing, check for slow/poison messages (DLQ). *Broker dies:* follower in ISR becomes leader. *Hot partition:* better key, add salt.

---

## 12. Ticket booking (seat locking)
> "Design a concert/movie ticket booking system."

**1. Requirements:** browse events, pick seats, hold seats for ~10 min while paying, no double booking, survive huge spikes (big concert sale).

**2. Estimates:** normal: low QPS. Big sale: 1M users in the first minutes for 50k seats.

**4. High-level design**
```
Users → CDN (static event pages) → Virtual waiting room (queue, admit N users/min)
      → Booking service → Seat hold (Redis: SET seat_id user NX EX 600) → Payment → confirm in DB (transaction)
Seats DB: seats(event_id, seat_id, status, booking_id, version)
```

**6. Deep dives**
- **No double booking:** hold with atomic `SET NX` + expiry, and confirm in DB with **optimistic locking** (`UPDATE seats SET status='BOOKED' WHERE seat_id=? AND status='HELD' AND held_by=?`) or a DB unique constraint on (event_id, seat_id).
- Holds expire automatically if payment not completed.
- **Waiting room** protects the system and is fair (FIFO).
- Bots: CAPTCHA, purchase limits per account.

**7. What-ifs:** *Payment succeeds after hold expired:* refund or re-check seat; extend hold during payment. *Redis down:* fall back to DB row locks (slower). *Spike 100× expected:* waiting room, static pages from CDN, autoscale.

---

## 13. Hotel / home rental booking
> "Design a booking system for hotels or home rentals (like Airbnb)."

- **Requirements:** search listings by location/dates/price, view availability, book without double booking, reviews, host calendar.
- **Design:** Search service (Elasticsearch with geo + filters; availability as a filter from a calendar index) → Listing service → Booking service with **availability table** `(listing_id, date, status)` → reserve dates in a DB transaction with row locks or unique constraint per (listing_id, date) → payment → confirmation. Read-heavy search vs strongly consistent booking → separate stores.
- **Trade-offs:** search index can be slightly stale (a listing might show available but fail at booking → re-check at booking, tell user).
- **What-ifs:** *Two guests book same dates:* constraint wins, second gets "no longer available". *Host changes price during checkout:* lock price quote with expiry. *Overbooking in hotels (intentional):* business rule with compensation flow.

---

## 14. Metrics & monitoring system
> "Design a system like Prometheus/Datadog that collects metrics from 100k servers."

- **Requirements:** collect metrics (CPU, latency, custom), store, query dashboards, alerting.
- **Estimates:** 100k hosts × 1,000 metrics every 10 s = **10M data points/s**.
- **Design:**
```
Agents on hosts → collectors (push) or scrapers (pull) → Kafka → ingesters → Time-series DB
  (compression: delta-of-delta timestamps, XOR floats; partition by metric + time)
Query service → dashboards;  Alert evaluator (rules every minute) → notification system
Downsampling: raw 10 s for 7 days → 1 min for 30 days → 1 h for 1 year
```
- **Deep dives:** **cardinality explosion** (labels like user_id create millions of series, so limit them), retention & downsampling, alert deduplication and routing.
- **What-ifs:** *Monitoring system down during an incident:* run it separately from what it monitors, multi-region. *Alert storm:* group alerts, dependency-aware alerting.

---

## 15. Distributed job scheduler
> "Design a system to run millions of scheduled/cron jobs."

- **Requirements:** schedule one-time and recurring jobs, run on time (±seconds), retries, no duplicate runs, visibility of status.
- **Design:**
```
API → Jobs DB (job_id, schedule, next_run_at, status)
Scheduler (leader-elected or partitioned by job_id hash): poll jobs where next_run_at <= now → push to queue
   → Workers execute → report status → update next_run_at
```
- **Deep dives:** avoid double runs with **leases** (`UPDATE ... SET owner=?, lease_until=? WHERE status='READY'`), idempotent jobs, time-bucketed index on `next_run_at`, priorities, retries with backoff, DLQ, timezone/DST handling.
- **What-ifs:** *Scheduler node dies:* lease expires, another picks the job. *Thundering herd at midnight:* jitter, spread start times. *Job runs longer than its interval:* skip or queue policy.

---

## 16. Real-time leaderboard
> "Top 100 players for a game with 50M players, updated in real time."

- **Design:** Redis **sorted set** (`ZADD leaderboard score user`, `ZREVRANGE 0 99`, `ZREVRANK user`) gives O(log n) updates. Persist scores in DB as source of truth.
- **Scale:** shard by score range or by region; global top-k = merge top-k of each shard. Daily/weekly boards = separate keys with TTL.
- **What-ifs:** *Redis lost:* rebuild from DB. *Cheating:* validate scores server-side. *Exact rank for millions:* approximate rank for low-ranked players (percentile buckets).

---

## 17. Proximity search (nearby places)
> "Find restaurants near me (like Yelp)."

- **Requirements:** search businesses within radius, filter by category/rating, read-heavy, business data changes rarely.
- **Design:** geo index (**geohash** prefixes, **quadtree**, or PostGIS / Elasticsearch geo queries) → fetch businesses in my cell + neighbours → filter by exact distance → rank (distance, rating, popularity). Read replicas + cache popular areas.
- **Difference from ride-hailing:** places don't move → index can be rebuilt daily and heavily cached; drivers move → in-memory, constantly updated.
- **What-ifs:** *Dense city returns too many results:* smaller cells / quadtree split. *Rural area returns none:* expand radius gradually.

---

## 18. Stock exchange / order matching
> (Brief. Asked mostly at fintech and trading firms.)

- **Core:** **order book** per symbol: buy orders sorted by price desc, sell orders by price asc, then by time (price-time priority). Matching engine is **single-threaded per symbol** for determinism and very low latency (microseconds), in memory.
- **Durability:** every incoming order written to a sequenced, replicated log before matching; engine state can be rebuilt by replaying the log; hot standby replicas consume the same log.
- **Around it:** risk checks before orders reach the engine, market data publishing (multicast), clearing/settlement after.
- **What-ifs:** *Engine crashes:* standby takes over from same log position. *Flash crash:* circuit breakers halt trading.

---

## 19. Email service
> "Design an email service like Gmail."

- **Requirements:** send/receive (SMTP), store mail, search, labels, attachments, spam filtering, huge storage.
- **Design:** inbound SMTP servers → spam/virus filtering (ML) → mail storage (metadata in wide-column DB sharded by user; bodies/attachments in object storage) → search index per user → IMAP/HTTP APIs → clients; outbound queue → SMTP to other servers with retries; reputation management (SPF, DKIM, DMARC).
- **What-ifs:** *Spam wave:* rate limit senders, update models, reputation blocks. *Receiving server down:* other MTAs retry (SMTP has built-in retries). *Big attachment:* store once, reference by ID.

---

## 20. CDN design
> "Design a content delivery network."

- **Components:** many edge **PoPs** worldwide with caches → regional/mid-tier caches → origin. Routing users to nearest healthy PoP via **anycast** or **GeoDNS**.
- **Caching:** cache key (URL + selected headers), TTL from `Cache-Control`, **purge/invalidation** API, versioned file names (`app.3f2a.js`) to avoid purges.
- **Deep dives:** request coalescing (one origin fetch for many concurrent misses), tiered caching to protect origin, TLS at edge, DDoS absorption, edge compute.
- **What-ifs:** *Bad file cached everywhere:* purge + versioned URLs. *Origin overloaded on cache expiry:* stale-while-revalidate, shielding tier. *One PoP down:* anycast reroutes automatically.

---

## 21. Patterns that repeat across cases
| Problem | Pattern | Seen in |
|---|---|---|
| Don't do the same thing twice | Idempotency keys, dedupe IDs | Payments, notifications, queues |
| Two users want the same thing | Atomic CAS / `SET NX` / unique constraint / optimistic locking | Tickets, rentals, ride matching |
| Huge read volume | Precompute + cache + CDN | Feed, autocomplete, video |
| Huge write volume | Append-only logs, LSM trees, batching, streaming aggregation | Metrics, KV store, view counts |
| Location queries | Geohash / quadtree / H3 | Ride-hailing, proximity |
| Spiky traffic | Queue + waiting room + autoscaling | Tickets, notifications |
| Slow work | Async workers via queue | Video transcoding, crawling |
| Must not lose money/data | Strong consistency, transactions, ledger, reconciliation | Payments, file metadata |
| Real-time two-way | WebSocket + per-entity server | Chat, docs, ride tracking |
| Event to many services reliably | Transactional outbox + Kafka | Payments, orders |

> **Interview tip:** after the basic design, always say: *"The hardest part of this system is ___, so let me go deeper there."* For feed it's fan-out, for tickets it's concurrency, for payments it's correctness, for ride-hailing it's location writes.
