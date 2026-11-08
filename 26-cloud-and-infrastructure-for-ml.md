# 26. Cloud & Infrastructure for ML

You don't need to be a cloud architect, but ML/AI engineers are expected to know how models run in the cloud, what GPUs cost, and what to do when infrastructure breaks.
MLOps practices are in [13-mlops.md](13-mlops.md); serving patterns in [02-ml-and-llm-systems.md](02-ml-and-llm-systems.md#4-model-serving).

### Contents
1. [Cloud basics](#1-cloud-basics)
2. [AWS vs GCP vs Azure service map](#2-aws-vs-gcp-vs-azure-service-map)
3. [Containers & Kubernetes for ML](#3-containers--kubernetes-for-ml)
4. [GPUs for training and inference](#4-gpus-for-training-and-inference)
5. [Ways to serve models in the cloud](#5-ways-to-serve-models-in-the-cloud)
6. [Networking & security basics](#6-networking--security-basics)
7. [Infrastructure as code & CI/CD](#7-infrastructure-as-code--cicd)
8. [Observability](#8-observability)
9. [Cost optimization](#9-cost-optimization)
10. [Interview Q&A](#10-interview-qa)
11. [What-if scenarios (cloud & infra)](#11-what-if-scenarios-cloud--infra)

---

## 1. Cloud basics
| Building block | What it is | ML use |
|---|---|---|
| **Compute** | VMs, containers, serverless functions | training jobs, model servers, batch jobs |
| **Storage** | Object (S3-like), block (disks), file (NFS) | datasets, model weights, checkpoints |
| **Databases** | Managed SQL/NoSQL, warehouses | metadata, features, analytics |
| **Networking** | VPC, subnets, load balancers, DNS | private, secure model endpoints |
| **IAM** | Identities, roles, policies | who/what can read data, deploy models |

- **Region** = geographic area; **Availability Zone (AZ)** = separate data center inside a region. Deploy across 2-3 AZs for high availability.
- **Shared responsibility:** the cloud secures the hardware; you secure your data, access, and configuration.
- **IaaS → PaaS → SaaS:** more managed = less control, less operations work.

## 2. AWS vs GCP vs Azure service map
| Need | AWS | GCP | Azure |
|---|---|---|---|
| VMs | EC2 | Compute Engine | Virtual Machines |
| Object storage | S3 | Cloud Storage (GCS) | Blob Storage / ADLS Gen2 |
| Managed Kubernetes | EKS | GKE | AKS |
| Serverless functions | Lambda | Cloud Functions / Cloud Run | Azure Functions / Container Apps |
| ML platform | SageMaker | Vertex AI | Azure Machine Learning |
| Managed LLM APIs | Bedrock | Vertex AI (Gemini + model garden) | Azure OpenAI / AI Foundry |
| Data warehouse | Redshift | BigQuery | Synapse / Fabric |
| Streaming | Kinesis / MSK (Kafka) | Pub/Sub / Dataflow | Event Hubs / Stream Analytics |
| Batch big data | EMR / Glue | Dataproc / Dataflow | HDInsight / Databricks |
| Orchestration | MWAA (Airflow) / Step Functions | Cloud Composer (Airflow) / Workflows | Data Factory |
| Container registry | ECR | Artifact Registry | ACR |
| Secrets | Secrets Manager | Secret Manager | Key Vault |
| Monitoring | CloudWatch | Cloud Monitoring / Logging | Azure Monitor |
| IAM | IAM roles/policies | IAM + service accounts | Entra ID + RBAC / managed identities |
| Vector search | OpenSearch, Aurora pgvector | Vertex AI Vector Search, AlloyDB pgvector | AI Search |

> **Interview tip:** say the concept first ("managed Kubernetes"), then the name for the cloud the company uses. Concepts transfer; names don't matter much.

## 3. Containers & Kubernetes for ML
- **Docker image** = code + dependencies + (sometimes) model. Pin versions; use slim base images; CUDA base images for GPU.
- **Kubernetes (K8s) basics:** **Pod** (running container(s)), **Deployment** (keeps N pods running, rolling updates), **Service** (stable network address), **Ingress** (HTTP routing), **ConfigMap/Secret**, **Job/CronJob** (batch), **Namespace** (isolation), **node pools** (groups of machines, e.g., GPU pool).
- **GPU scheduling:** NVIDIA device plugin exposes `nvidia.com/gpu`; request it in pod spec; use **taints/tolerations** so only GPU workloads land on expensive GPU nodes; **MIG / time-slicing** to share one GPU between small models.
- **Autoscaling:**
  - **HPA:** more pods based on CPU/GPU/custom metrics (QPS, queue length, latency).
  - **Cluster autoscaler / Karpenter:** more nodes when pods can't be scheduled.
  - **KEDA:** scale on events (queue depth), including **scale to zero**.
- **ML serving on K8s:** **KServe**, Seldon, Ray Serve, BentoML, Triton, vLLM/TGI containers. Features: canary rollouts, autoscaling, model versioning, request batching.
- **Training on K8s:** Kubeflow Training Operator, Ray, Volcano/Kueue (gang scheduling, so all GPUs for a distributed job start together or not at all).
- **Health probes:** *readiness* (ready for traffic after model loaded) vs *liveness* (restart if stuck). A big model needs a long startup/readiness time or it gets killed in a loop.

## 4. GPUs for training and inference
| Topic | Key points |
|---|---|
| Why GPUs | Thousands of cores for parallel matrix math; high memory bandwidth |
| Families (examples) | Data-center: A100, H100/H200, B200 (training + big LLM inference); L4, A10G, T4 (cheaper inference) |
| **Memory is usually the limit** | Model weights + activations + optimizer states (training) or KV cache (LLM inference) |
| Training memory rule | Full fine-tune with Adam in mixed precision ≈ 16-20 bytes/parameter → 7B model ≈ 120-140 GB → multiple GPUs or LoRA/QLoRA |
| Inference memory rule | FP16 = 2 bytes/param (7B ≈ 14 GB) + KV cache; INT4 ≈ 0.5 byte/param |
| Multi-GPU | Data parallel (DDP), FSDP/ZeRO, tensor & pipeline parallel; fast interconnect (NVLink, InfiniBand) matters |
| Utilization | Watch GPU util %, memory, SM occupancy; low util usually = data loading bottleneck or small batches |
| Alternatives | TPUs (GCP), AWS Trainium/Inferentia, CPUs for small models |
| Cost | GPUs are the biggest ML cost line, and idle GPUs are the #1 waste |

## 5. Ways to serve models in the cloud
| Option | Good for | Trade-off |
|---|---|---|
| Managed endpoint (SageMaker / Vertex / Azure ML) | Fast start, built-in autoscaling & monitoring | Less control, platform cost |
| Kubernetes (KServe, vLLM) | Many models, custom needs, cost control at scale | You operate it |
| Serverless containers (Cloud Run, Lambda, Container Apps) | Spiky/low traffic, small CPU models, scale to zero | Cold starts, limited GPU support, size limits |
| Serverless GPU providers / managed LLM APIs | LLMs without running GPUs | Per-token cost, vendor dependency |
| Batch jobs (Spark, Batch services) | Precompute predictions | Not real-time |
| Edge / on-device | Privacy, offline, very low latency | Small models only |

## 6. Networking & security basics
- **VPC:** your private network in the cloud. **Public subnet** (internet-facing load balancers) vs **private subnet** (model servers, databases).
- **Private endpoints / PrivateLink / Private Service Connect:** reach cloud services (storage, LLM APIs) without going over the public internet. Often required for sensitive data.
- **Security groups / firewall rules:** allow only needed ports and sources.
- **API gateway** in front of models: auth, rate limits, quotas, logging.
- **IAM least privilege:** training job role can read only its dataset bucket; serving role can read only the model registry. Use **workload identity** (no long-lived keys in code).
- **Encryption:** in transit (TLS) and at rest (KMS-managed keys, customer-managed keys for regulated industries).
- **Secrets:** in a secrets manager, injected at runtime. Never put them in images, code, notebooks, or prompts.
- **Data residency:** some data must stay in a country/region → choose region and LLM endpoints accordingly.

## 7. Infrastructure as code & CI/CD
- **IaC:** Terraform / OpenTofu, Pulumi, CloudFormation, Bicep. Infra is reviewed in pull requests, reproducible, versioned; avoid manual console changes ("click-ops") which cause drift.
- **CI:** lint, unit tests, data/model tests, build image, security scan of image and dependencies.
- **CD:** deploy to staging → automated checks → canary in production → full rollout; GitOps (Argo CD / Flux) keeps cluster state equal to git.
- **Environments:** dev / staging / prod in separate accounts/projects for blast-radius control.

## 8. Observability
- **Metrics:** latency p50/p95/p99, QPS, error rate, GPU util/memory, queue depth, tokens/s, cost.
- **Logs:** structured JSON with request IDs; redact PII.
- **Traces:** OpenTelemetry across gateway → service → model → vector DB.
- **Dashboards & alerts** on SLOs (e.g., p95 < 500 ms for 99% of 5-min windows), not on every metric.
- ML-specific monitoring (drift, quality) in [13](13-mlops.md) and [02 §6](02-ml-and-llm-systems.md#6-monitoring-ml-systems).

## 9. Cost optimization
| Lever | How |
|---|---|
| **Spot / preemptible instances** | 60-90% cheaper; for training with checkpointing, batch jobs; not for critical online serving alone |
| **Reserved instances / savings plans / committed use** | Discount for steady baseline load |
| **Autoscaling & scale to zero** | No idle GPUs at night; KEDA, serverless |
| **Right-sizing** | Smaller GPU (L4 vs H100) for inference; CPU for small models |
| **Model optimization** | Quantization, distillation, batching, caching (see [02 §8](02-ml-and-llm-systems.md#8-llm-serving--optimization)) |
| **Storage tiers & lifecycle rules** | Move old datasets/checkpoints to cold storage, delete temp data |
| **Data transfer** | Keep compute next to data (same region); egress costs money |
| **Visibility** | Tags/labels per team/project, budgets, alerts, cost dashboards (FinOps) |

## 10. Interview Q&A

**Q: How would you deploy a PyTorch model as a scalable API?** Package with a model server (FastAPI/TorchServe/Triton) in a Docker image → push to registry → deploy on managed endpoint or K8s (Deployment + Service + HPA) behind a load balancer/API gateway → readiness probe after model load → canary rollout → metrics, logs, alerts.

**Q: How do you train a model that needs 8 GPUs for 3 days without wasting money?** Spot instances with frequent checkpointing to object storage and automatic resume; gang scheduling; profile first on a small run; data in same region; mixed precision; shut everything down automatically at the end.

**Q: Managed ML platform vs Kubernetes?** Managed: faster, less ops, good for small teams. K8s: flexibility, many models, cheaper at scale, needs platform engineers. Many companies mix: managed training, K8s serving.

**Q: How do you keep secrets out of code?** Secrets manager + workload identity; scan repos for secrets in CI; rotate keys.

**Q: How do you make a model endpoint highly available?** Multiple replicas across AZs, health checks, autoscaling with minimum replicas, graceful degradation/fallback model, multi-region for critical systems.

**Q: Cold start problem?** Container start + model download/load can take minutes for big models. Fixes: min replicas warm, bake weights in image or cache on node-local disk, faster formats (safetensors), lazy load, smaller models.

## 11. What-if scenarios (cloud & infra)

### GPU quota or capacity is not available in our region
**Mitigate now:** use another GPU type or region (if data rules allow), queue the training job, use smaller model/LoRA to fit smaller GPUs. **Long-term:** request quota early, reserved capacity/commitments for critical needs, multi-region/multi-cloud capability, portable containers.

### Pods are stuck in "Pending"
**Causes (ranked):** not enough nodes/GPUs (cluster autoscaler at max or no capacity), resource requests too big for any node, taints without matching tolerations, node selector/affinity mismatch, quota limits per namespace, PVC can't attach (volume in another zone).
**Isolate:** `kubectl describe pod` → Events section tells the reason.
**Fix:** adjust requests, add node pool, fix tolerations/selectors, raise quota.

### Cloud bill doubled this month
**Isolate:** cost explorer by service → by tag/team → by resource. **Usual causes:** forgotten GPU instances/endpoints, autoscaling min too high, egress (cross-region traffic), logs volume explosion, storage of old checkpoints, runaway LLM API usage.
**Fix:** stop idle resources, lifecycle rules, budgets + alerts, auto-shutdown for notebooks, per-team quotas. **Prevent:** cost dashboards reviewed weekly, tagging enforced by policy.

### The whole region has an outage
**Depends on design:** single-region → service down (state the RTO/RPO honestly). Better: multi-AZ always; for critical systems, warm standby in a second region with replicated data, DNS failover, models and images replicated across regions, tested runbooks (game days).

### New pods take 8 minutes to start because the model downloads every time
**Fix:** cache weights on node-local SSD or a shared volume, pre-pull images (DaemonSet), bake model into image for small models, use faster storage and parallel download, keep min warm replicas, readiness probe set correctly so traffic waits.

### An API key / cloud secret was pushed to a public GitHub repo
**This is an incident. Act in minutes:** revoke/rotate the key immediately, check access logs for misuse, remove from git history (but assume it's already copied), check billing for abuse (crypto mining is common). **Prevent:** secret scanning in CI and pre-commit hooks, short-lived credentials via workload identity, no long-lived keys.

### Latency is fine in one AZ but bad in another
Cross-AZ calls (model in AZ-a, vector DB in AZ-b), noisy neighbours, uneven load balancing. Fix: zone-aware routing, colocate dependent services, check LB health checks.

### Training job keeps getting killed on spot instances
This is expected, so design for it: checkpoint every N minutes, auto-resume, mix of spot + on-demand for the coordinator, diversify instance types.
