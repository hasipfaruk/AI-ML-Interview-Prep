# 20. Graph Machine Learning

Graphs show up in many interviews in fraud detection, recommendations, social networks, drug discovery, knowledge graphs and GraphRAG.
Format: **Q → short answer you can say in 30-60 seconds**, then "what if" scenarios at the end.

### Contents
1. [Graph basics](#1-graph-basics)
2. [Graph tasks](#2-graph-tasks)
3. [Classic graph features](#3-classic-graph-features)
4. [Node embeddings: DeepWalk and node2vec](#4-node-embeddings-deepwalk-and-node2vec)
5. [Graph neural networks (GNNs)](#5-graph-neural-networks-gnns)
6. [Training and scaling GNNs](#6-training-and-scaling-gnns)
7. [Knowledge graphs](#7-knowledge-graphs)
8. [GraphRAG](#8-graphrag)
9. [Use cases and system design](#9-use-cases-and-system-design)
10. [What-if scenarios](#10-what-if-scenarios)

---

## 1. Graph basics

**Q: What is a graph?** A set of **nodes** (entities: users, products, molecules' atoms) and **edges** (relationships: follows, bought, bonded). Nodes and edges can have features.

**Q: Directed vs undirected?** Directed edges have a direction (A follows B). Undirected edges are mutual (A is friends with B).

**Q: Weighted vs unweighted?** Weighted edges carry a strength (number of transactions, distance).

**Q: Homogeneous vs heterogeneous graph?** Homogeneous: one node type and one edge type. Heterogeneous: many types (user, item, merchant; edges "bought", "reviewed", "shares-device-with"). Most real business graphs are heterogeneous.

**Q: Bipartite graph?** Two node types, edges only between types (users ↔ items). The standard shape for recommender data.

**Q: How do you store a graph in memory?**
| Format | Good for |
|---|---|
| Adjacency matrix (N × N) | small dense graphs, math |
| Adjacency list | sparse graphs, traversal |
| Edge list (src, dst) | storage, input to GNN libraries |
| CSR (compressed sparse row) | fast neighbor lookup at scale |

**Q: Degree?** Number of edges of a node. In-degree / out-degree for directed graphs. Real graphs have a **power-law degree distribution**: a few "hub" nodes with huge degree.

**Q: Graph databases?** Neo4j, Amazon Neptune, TigerGraph, JanusGraph. They store nodes and edges natively and support traversal queries (Cypher, Gremlin). Use them when the core queries are multi-hop relationships.

**Q: Homophily vs heterophily?** Homophily: connected nodes tend to be similar (friends share interests). Heterophily: connected nodes tend to differ (fraudsters connect to normal users). Many simple GNNs assume homophily and do worse on heterophily.

## 2. Graph tasks

| Level | Task | Example |
|---|---|---|
| **Node** | classify / regress a node | Is this account a fraudster? |
| **Edge (link)** | predict if an edge exists / its type | Will user buy item? Friend suggestion? Drug-target interaction? |
| **Graph** | classify a whole graph | Is this molecule toxic? |
| **Community** | find groups | Fraud rings, customer segments |
| **Generation** | create new graphs | New molecules |

**Q: Transductive vs inductive learning?** Transductive: all nodes (including test nodes) are present during training; can't handle new nodes without retraining (e.g., classic node2vec, basic GCN). Inductive: learns a function that works on unseen nodes/graphs (GraphSAGE). **Production systems with new users every minute need inductive models.**

**Q: How do you split data for link prediction?** Hide a fraction of edges as positives for validation/test, sample non-edges as negatives, and make sure hidden edges are **removed from the graph used for message passing**. Otherwise the model sees the answer (leakage). For time-based data, split by time.

## 3. Classic graph features

Before GNNs, and still very strong as features for gradient-boosted trees.

**Q: Degree centrality?** Number of neighbors (popularity).

**Q: Betweenness centrality?** How often a node lies on shortest paths between others ("bridges" and brokers). Expensive to compute exactly on big graphs.

**Q: Closeness centrality?** How close a node is to everyone else (inverse of average distance).

**Q: PageRank?** A node is important if important nodes link to it. Computed by a random walk with a damping factor (~0.85 chance to follow a link, 0.15 to jump randomly). Used for web ranking, influencer detection, fraud scoring (personalized PageRank from known fraudsters).

**Q: Personalized PageRank?** Random walk that restarts at specific seed nodes → scores how close every node is to the seeds. Great for "who is related to these known bad accounts?" and for recommendations.

**Q: Clustering coefficient?** How many of a node's neighbors are also connected to each other. It measures tight groups.

**Q: Community detection algorithms?** Louvain / Leiden (maximize modularity, fast, most used), label propagation (very fast), connected components (simplest, and often enough for fraud rings that share a device or card).

**Q: Common neighbors / Jaccard / Adamic-Adar?** Simple link prediction scores: two nodes with many shared neighbors are likely to connect. Strong baselines for friend suggestions.

**Q: Why mention classic features in an interview?** Because they are cheap, explainable, and often beat a GNN on a small budget. A good answer: *"I'd start with graph features (degree, PageRank, component size, shared-device counts) in XGBoost as a baseline, then try a GNN if it adds lift."*

## 4. Node embeddings: DeepWalk and node2vec

**Q: What is a node embedding?** A vector per node so that similar/connected nodes are close in vector space. Used as features or for nearest-neighbor search.

**Q: DeepWalk?** Do random walks on the graph, treat each walk as a "sentence" of node IDs, train Word2Vec (skip-gram) on them. Nodes that appear in similar walks get similar vectors.

**Q: node2vec?** DeepWalk with **biased** random walks controlled by p (return) and q (in-out). Low q → explore far (DFS-like, captures communities/homophily). High q → stay local (BFS-like, captures structural roles).

**Q: Limitations of DeepWalk/node2vec?** Transductive (new node → no embedding without retraining), ignore node features, one embedding per node means memory grows with graph size.

**Q: Matrix factorization view?** These methods are approximately factorizing a matrix of node co-occurrence, the same idea as collaborative filtering.

## 5. Graph neural networks (GNNs)

**Q: Core idea of a GNN: message passing?** Each layer, every node:
1. collects messages from its neighbors (their current vectors),
2. **aggregates** them (sum, mean, max, attention),
3. **updates** its own vector by combining with its previous vector through a small neural network.
After k layers, a node's vector contains information from its **k-hop neighborhood**.

```
h_v(new) = UPDATE( h_v , AGGREGATE( { h_u : u in neighbors(v) } ) )
```

**Q: Why not just use a normal neural network on the adjacency matrix?** Graphs have no fixed size or node order. GNNs are **permutation invariant/equivariant** (reordering nodes doesn't change results), and they share weights across nodes.

**Q: GCN (Graph Convolutional Network)?** Aggregates neighbors with a normalized average (by degree), then a linear layer + non-linearity: `H' = σ(D^-½ (A+I) D^-½ H W)`. Simple and strong on homophilous graphs. Transductive in its original form (needs the full graph).

**Q: GraphSAGE?** Samples a fixed number of neighbors per node and learns aggregator functions (mean, pooling, LSTM). **Inductive**: works for new nodes from their features and neighbors. Built for huge graphs (originally Pinterest-scale ideas → PinSage).

**Q: GAT (Graph Attention Network)?** Learns attention weights for each neighbor, so important neighbors matter more. Helps when neighbors vary in relevance.

**Q: GIN (Graph Isomorphism Network)?** Uses sum aggregation + MLP; as expressive as the Weisfeiler-Lehman graph isomorphism test. Good for graph-level tasks (molecules).

**Q: Heterogeneous GNNs (R-GCN, HAN, HGT)?** Separate weights per edge type / node type, so "bought" and "reviewed" edges are treated differently.

**Q: Temporal GNNs?** For graphs that change over time (transactions): TGN, TGAT. They include edge timestamps and memory per node. Useful for fraud where order of events matters.

**Q: How do you do graph-level prediction?** Run message passing, then a **readout/pooling** (sum/mean/max of node vectors, or hierarchical pooling) → classifier.

**Q: Link prediction with GNN?** Compute node embeddings, then score a pair with dot product or an MLP on [h_u, h_v]. Train with positive edges and sampled negative edges.

**Q: Over-smoothing?** With many layers, all node vectors become similar (every node has averaged over the whole graph) → performance drops. That's why most GNNs use only **2-3 layers**. Fixes: residual/skip connections, jumping knowledge (combine all layers), normalization (PairNorm), DropEdge.

**Q: Over-squashing?** Information from many distant nodes gets compressed into a fixed-size vector through bottleneck edges → long-range signals are lost. Fixes: graph rewiring, adding virtual nodes, graph transformers.

**Q: Graph Transformers?** Full attention across nodes with positional encodings from graph structure (Laplacian eigenvectors, random-walk encodings). Handle long-range dependencies but cost O(N²), so they are used on small/medium graphs (molecules).

**Q: Expressiveness limit of message-passing GNNs?** They can't distinguish some different graphs (bounded by the 1-WL test). Adding node IDs, positional encodings, or subgraph features helps.

## 6. Training and scaling GNNs

**Q: Why are GNNs hard to scale?** Neighborhood explosion: with 2 layers and 100 neighbors each, one node needs 10,000 nodes' features. Full graph won't fit in GPU memory for billions of edges.

**Q: Solutions?**
| Technique | How it works |
|---|---|
| **Neighbor sampling** (GraphSAGE) | sample e.g. 15 then 10 neighbors per layer |
| **Cluster-GCN / GraphSAINT** | train on subgraphs (clusters or sampled subgraphs) |
| **Precomputation (SIGN, SGC)** | precompute aggregated features offline, then a simple MLP; very fast inference |
| **Distributed training** | partition graph across machines (DistDGL, PyG distributed) |
| **Historical embeddings / caching** | reuse stale neighbor embeddings |

**Q: Libraries?** PyTorch Geometric (PyG), DGL, GraphStorm; graph databases or Spark GraphFrames for features.

**Q: Online inference for GNNs: what makes it hard?** At request time you need the node's neighborhood and their features fast. Options: precompute embeddings in batch (daily/hourly) and store in a feature store/vector DB; for new nodes use an inductive model with sampled neighbors from a graph store; cap neighbor count for latency.

**Q: Negative sampling for link prediction?** Random negatives are too easy. Use **hard negatives** (nodes 2-3 hops away, popular items) to make the model learn fine distinctions. Evaluate with ranking metrics (MRR, Hits@K) not just AUC.

**Q: Class imbalance in node classification (fraud = 0.1%)?** Weighted loss, oversampling minority nodes' neighborhoods, focal loss, threshold tuning, evaluate with PR-AUC. See [07 §8](07-ml-fundamentals.md#8-data-preparation--feature-engineering).

## 7. Knowledge graphs

**Q: What is a knowledge graph (KG)?** Facts stored as triples **(head, relation, tail)**: (Paris, capital_of, France). Wikidata, product graphs, enterprise KGs.

**Q: How do you build a KG from text?** Named entity recognition → entity linking (map "Apple" to the right entity) → relation extraction (rules, fine-tuned models, or LLMs with structured output) → deduplication / entity resolution → store in graph DB → human review for high-value facts.

**Q: KG embeddings?**
- **TransE:** relation is a translation: h + r ≈ t. Simple, fails on 1-to-many relations.
- **DistMult / ComplEx:** multiplicative scores; ComplEx handles asymmetric relations.
- **RotatE:** relation is a rotation in complex space.
Used for **link prediction / KG completion** (predict missing facts).

**Q: Entity resolution?** Deciding that "IBM", "I.B.M." and "International Business Machines" are the same entity. Blocking (cheap candidate pairs) + similarity model + clustering. Critical for fraud graphs (same person, different names).

**Q: Ontology / schema?** Defines allowed entity types and relations. Keeps the KG consistent.

## 8. GraphRAG

**Q: What is GraphRAG?** RAG that uses a graph built from the documents: extract entities and relations with an LLM, build a KG, optionally detect communities and summarize each, then retrieve **entities + their neighborhoods + community summaries** in addition to (or instead of) text chunks. Plain RAG basics are in [02 §7](02-ml-and-llm-systems.md#7-llm-systems-rag-in-depth).

**Q: When does GraphRAG beat normal vector RAG?**
- Multi-hop questions ("Which suppliers of our top customer had compliance issues?"). See [04 #10](04-what-if-scenarios.md).
- Global/summary questions over a whole corpus ("What are the main themes in these 5,000 reports?").
- Domains with many entities and relations (legal, biomedical, supply chain).

**Q: Downsides?** Expensive indexing (many LLM calls to extract entities), extraction errors and duplicate entities, harder to keep fresh, more complex pipeline. For simple fact lookup, hybrid vector + keyword RAG is usually enough.

**Q: Text-to-graph-query?** LLM converts the question into Cypher/SPARQL and runs it on the KG. Precise for structured questions; risky if schema is complex → give the schema in the prompt, validate the query, limit results.

## 9. Use cases and system design

| Use case | Graph | Task | Typical approach |
|---|---|---|---|
| **Fraud rings** | accounts, devices, cards, IPs, addresses | node classification, community detection | shared-attribute edges → connected components + graph features in XGBoost → GNN (often temporal, heterogeneous) |
| **Recommendations** | user-item bipartite (+ social) | link prediction | PinSage/LightGCN-style embeddings → ANN candidate generation → ranker. See [05 #4](05-case-studies.md#4-recommendation-system) |
| **Social networks** | users, follows | friend suggestion, influence, spam | common neighbors, PPR, GNN embeddings |
| **Drug discovery** | molecules (atoms/bonds), protein interaction graphs | graph property prediction, link prediction | GIN / graph transformers / KG embeddings |
| **Supply chain / risk** | companies, suppliers | risk propagation | KG + PageRank-style propagation |
| **Maps / ETA** | road network | travel time | GNN over road segments |
| **Search / Q&A** | knowledge graph | entity answers | KG lookup + GraphRAG |

**Mini system design: real-time fraud ring detection**
```
Events (signups, logins, payments) → Kafka → Graph builder (stream)
   → Graph store (accounts ↔ device / card / IP / address edges)
   → Streaming features: component size, # accounts per device, distance to known fraud (PPR)
   → Online scorer: XGBoost on graph + tabular features (fast)
   → Offline: daily GNN embeddings (heterogeneous, temporal) → feature store
   → Investigator UI shows the ring visually (explainability)
```
Trade-offs to mention: real-time graph updates vs. batch embeddings, hub nodes (a public Wi-Fi IP connects thousands of honest users, so cap or down-weight hubs), privacy of linked data.

---

## 10. What-if scenarios

### GNN performs worse than a simple XGBoost on tabular features.
**Causes (ranked):** graph edges are noisy or not predictive; heterophily (neighbors differ from the node, so averaging hurts); leakage-free split made the task honest while the tabular model leaks; over-smoothing from too many layers; poor hyperparameters.
**Isolate:** measure homophily of the labels; try 1-layer vs 2 vs 3; add graph features (degree, PageRank) to XGBoost and see if they help.
**Fix:** use graph features in XGBoost (often the best production answer); heterophily-aware GNNs (separate self and neighbor embeddings, e.g., GraphSAGE concat, H2GCN); better edge definitions.
**Prevent:** always keep a strong non-graph baseline in the eval.

### Accuracy drops when you add more GNN layers.
Over-smoothing (or over-squashing). Keep 2-3 layers, add residual / jumping-knowledge connections, normalization, DropEdge.

### Link prediction AUC is 0.99 offline but recommendations are bad online.
**Causes:** test edges leaked into the message-passing graph; random negatives are too easy; random split instead of time split; AUC doesn't reflect ranking quality.
**Fix:** remove test edges from the training graph, time-based split, hard negatives, evaluate with Hits@K / MRR / recall@K on future interactions.

### Training runs out of GPU memory on a 1-billion-edge graph.
Neighbor sampling (fanout 10-15 per layer), subgraph training (Cluster-GCN/GraphSAINT), precomputed aggregations (SIGN), store features on CPU/disk with GPU caching, distributed training with graph partitioning.

### New users/items get no embedding (cold start).
Transductive model (node2vec, original GCN). Switch to an **inductive** model (GraphSAGE) that uses node features, or fall back to feature-only embeddings until the node has edges.

### Fraud graph flags thousands of honest users as one "ring".
**Cause:** hub nodes (a shared public IP, a big office, a payment gateway, a default device ID) connect unrelated users.
**Fix:** remove or down-weight high-degree hub nodes, use edge types with stronger meaning (same card > same IP), time windows on edges, human review for large components.

### Online GNN scoring is too slow (needs 2-hop neighbors in real time).
Precompute embeddings in batch and serve from a feature store; cap neighbors; use 1 hop online + precomputed neighbor embeddings; simpler precomputed models (SGC/SIGN) for inference.

### Knowledge graph has many duplicate entities.
Weak entity resolution. Add blocking + similarity model + human review queue, canonical IDs, merge rules; measure duplicate rate as a data-quality metric.

### GraphRAG gives wrong answers about relationships.
**Causes:** LLM extraction errors (wrong relation, wrong entity linking), stale graph, missing edges.
**Isolate:** trace the answer back to the triples used; check them against the source text.
**Fix:** store source-text provenance for every triple, verify triples with a second pass, confidence scores, refresh pipeline on document change, combine with text-chunk retrieval as evidence.

### The graph changes every second, but embeddings update daily.
Hybrid: real-time graph features (counts, component membership) computed in streaming + daily embeddings; temporal GNNs with per-node memory if the budget allows; monitor how stale embeddings affect metrics.
