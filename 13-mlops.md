# 13 — MLOps & Production ML (Q&A)

Complements [02-ml-and-llm-systems.md](02-ml-and-llm-systems.md). Asked heavily in ML Engineer / MLOps / AI Engineer interviews.

## Core Q&A

**Q: What is MLOps?** Practices to reliably build, deploy, monitor and improve ML models in production: CI/CD for code **and** data **and** models, reproducibility, automation, monitoring.

**Q: How is ML CI/CD different from software CI/CD?**
Software: test code → deploy. ML adds: data validation, training pipeline, model evaluation gates (must beat current model), model registry, continuous training (CT), and monitoring of data/model quality — not just uptime.

**Q: MLOps maturity levels?** Level 0: manual notebooks. Level 1: automated training pipeline + continuous training. Level 2: full CI/CD of pipelines with automated testing, deployment and monitoring.

**Q: What should you version?** Code (git), data (DVC/lakeFS/Delta), features, model artifacts (registry), hyperparameters/config, environment (Docker image, requirements lock), prompts (for LLMs), eval datasets.

**Q: Tools you should know by name?**
| Need | Tools |
|---|---|
| Orchestration | Airflow, Kubeflow Pipelines, Prefect, Dagster, SageMaker/Vertex Pipelines |
| Experiment tracking | MLflow, Weights & Biases, Neptune |
| Feature store | Feast, Tecton, Databricks/Vertex/SageMaker feature stores |
| Model registry | MLflow Registry, SageMaker/Vertex registries |
| Serving | Triton, TorchServe, BentoML, KServe, Ray Serve, vLLM/TGI (LLMs) |
| Containers | Docker, Kubernetes (autoscaling, GPU scheduling) |
| Monitoring | Prometheus + Grafana, Evidently, Arize, WhyLabs; LLM: Langfuse, LangSmith, Phoenix |
| Data quality | Great Expectations, dbt tests, Pandera |

**Q: How do you test ML systems?**
- Unit tests for feature code and preprocessing.
- Data tests: schema, ranges, nulls, distribution.
- Model tests: performance thresholds on holdout, slice tests (no segment worse than X), invariance tests (changing a name shouldn't change sentiment), directional tests, regression tests on known hard cases.
- Integration tests: end-to-end pipeline on sample data.
- Load tests: latency/throughput of serving.

**Q: Deployment strategies?** Shadow → canary → A/B → full; blue-green; keep previous version for instant rollback. See [02 §5](02-ml-and-llm-systems.md#5-deployment--experimentation).

**Q: Online vs batch inference trade-offs?** See [02 §4](02-ml-and-llm-systems.md#4-model-serving).

**Q: How to make inference cheaper/faster?** Batching, quantization, distillation, pruning, ONNX/TensorRT compilation, caching predictions, right-sizing hardware (CPU often enough for small models), autoscaling, spot instances for batch.

**Q: How do you containerize and scale a model?** Docker image with model + server, health/readiness endpoints, deploy on Kubernetes with HPA (autoscale on CPU/GPU/QPS/queue length), resource limits, GPU node pools, model loaded at startup (or pulled from registry).

**Q: Continuous training triggers?** Schedule, new labeled data volume, drift detected, performance drop.

**Q: What is training-serving skew and how to prevent it?** See [04 #23](04-what-if-scenarios.md#23-model-accuracy-was-95-offline-but-70-in-production): shared feature code/feature store, log serving features and use them for training, compare distributions.

**Q: Feedback loops?** Model's predictions affect future training data (recommenders only learn from items shown). Mitigate with exploration, randomized holdouts, logging propensities.

**Q: Responsible AI in production?** Fairness checks by slice, explainability, model cards, data privacy (PII handling, retention), audit trails, human oversight for high-stakes decisions.

**Q: LLMOps — what's different?** Prompt versioning, eval suites with LLM judges, token cost monitoring, tracing multi-step chains/agents, guardrails, provider fallback, managing model version changes from vendors, RAG index pipelines.

## What-if scenarios (MLOps)
- **Training pipeline fails at 3 AM** → alerting, retries for transient errors, idempotent steps, checkpointing; keep serving the previous model (never block serving on training).
- **Model registry has a model but no one knows what data it used** → enforce lineage metadata on registration (data version, code commit, metrics) in the pipeline; block manual uploads.
- **Kubernetes pods with the model restart constantly (OOMKilled)** → memory limits too low for model + batch, memory leak, too many workers each loading the model; right-size, share model across workers, smaller batch.
- **Cold starts take 2 minutes** → bake model in image or fast storage, keep min replicas, lazy-load less used models, smaller model formats.
- **Multiple teams deploy models differently, causing chaos** → internal ML platform: templates, standard serving, registry, monitoring defaults (paved road).
- **Cloud bill doubled** → find idle GPUs, oversized instances, unused endpoints, untagged experiments; autoscale to zero, spot/preemptible for training, budgets & alerts per team.
