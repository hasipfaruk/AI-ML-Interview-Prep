# 27. Security, Privacy & Responsible AI

Senior AI/ML interviews almost always include a question like *"How would you make this safe?"*, *"What could an attacker do?"* or *"How do you make sure the model is fair?"*.
This chapter gives you the vocabulary and the structured answers. Related: [04 #7](04-what-if-scenarios.md#7-users-see-documents-they-shouldnt-have-access-to), [04 #15](04-what-if-scenarios.md#15-prompt-injection-a-user-made-the-bot-reveal-its-system-prompt--ignore-rules), [04 #20](04-what-if-scenarios.md#20-outputs-contain-pii-emails-phone-numbers-of-other-customers), [22 §8](22-ai-agents.md#8-safety-human-in-the-loop-sandboxing-permissions).

> Note: laws differ by country and change often. In interviews, describe principles and say you would work with legal/compliance teams. Never claim a design is "fully compliant" on your own.

### Contents
1. [Threat modeling for ML and LLM systems](#1-threat-modeling-for-ml-and-llm-systems)
2. [Attacks on LLM applications](#2-attacks-on-llm-applications)
3. [Attacks on ML models and data](#3-attacks-on-ml-models-and-data)
4. [Supply chain security](#4-supply-chain-security)
5. [Defenses checklist](#5-defenses-checklist)
6. [Privacy](#6-privacy)
7. [Fairness](#7-fairness)
8. [Explainability and transparency](#8-explainability-and-transparency)
9. [Regulation and risk tiers](#9-regulation-and-risk-tiers)
10. [AI governance inside a company](#10-ai-governance-inside-a-company)
11. [What-if scenarios](#11-what-if-scenarios)

---

## 1. Threat modeling for ML and LLM systems

**Q: What is threat modeling?** Systematically asking: *What are we protecting (assets)? Who might attack (actors)? How (attack surface)? What happens if they succeed (impact)? What stops them (controls)?*

**Q: Assets in an AI system?** Training data, user data and conversations, model weights, system prompts and business logic, tool credentials, the model's decisions (loans, moderation), compute budget.

**Q: Attack surface of an LLM app?** User input, uploaded files, retrieved documents, web pages and emails the agent reads, tool outputs, third-party models/plugins, training data sources, the model API itself, logs.

**Q: A simple framework to use in interviews?** Walk the pipeline (same layer map as [03](03-debugging-framework.md)) and for each layer ask about **C-I-A**: Confidentiality (can data leak?), Integrity (can someone change data or behavior?), Availability (can someone make it slow/expensive/down?).

**Q: Known reference lists?** There are public community lists of top LLM application risks (prompt injection, sensitive information disclosure, supply chain, data and model poisoning, improper output handling, excessive agency, system prompt leakage, vector/embedding weaknesses, misinformation, unbounded consumption) and knowledge bases of adversarial ML tactics. Mentioning that you use such checklists sounds senior.

## 2. Attacks on LLM applications

| Attack | What happens | Main defenses |
|---|---|---|
| **Direct prompt injection / jailbreak** | user tricks model into ignoring rules | layered guardrails, safe model, never rely on the prompt for security |
| **Indirect prompt injection** | hidden instructions in documents, web pages, emails, tool results | treat retrieved content as untrusted, approval for actions, limit outbound channels |
| **Sensitive data disclosure** | model reveals PII, secrets, other tenants' data | data minimization, ACL pre-filtering, output PII filters, no secrets in prompts |
| **System prompt leakage** | attacker extracts instructions | assume prompts are public; keep secrets and auth logic out |
| **Insecure output handling** | model output used directly in SQL, shell, HTML → injection/XSS | treat output as untrusted input: escape, parameterize, validate |
| **Excessive agency** | agent has more permissions than needed | least privilege, approvals, scoped tokens ([22 §8](22-ai-agents.md#8-safety-human-in-the-loop-sandboxing-permissions)) |
| **Denial of wallet / resource abuse** | huge prompts, loops, bots burn your budget | rate limits, token quotas, max steps, abuse detection |
| **Vector store attacks** | poisoned documents planted to be retrieved; cross-tenant leakage | ingestion controls, provenance, tenant isolation |
| **Data exfiltration via rendering** | model outputs an image/link URL containing secrets that the client auto-loads | block or proxy external URLs in rendered output |

**Q: Can prompt injection be fully solved today?** No. Say: *"I treat it like phishing. I reduce the chance with classifiers and good prompting, but design the system so a successful injection has limited impact."*

## 3. Attacks on ML models and data

**Q: Data poisoning?** Attacker inserts bad training examples to degrade the model or plant a **backdoor** (a trigger pattern that causes a chosen output, e.g., a small sticker makes a stop sign "speed limit"). Risk sources: scraped web data, user feedback loops, crowd labels, public datasets.
**Defenses:** data provenance and trusted sources, anomaly/outlier detection on training data, label audits, limiting the weight of any single user's feedback, robust training, testing for backdoor triggers, keeping clean holdout sets.

**Q: Adversarial examples (evasion)?** Tiny, often invisible input changes that flip a prediction (image noise, character swaps in text, feature manipulation in fraud).
**Defenses:** adversarial training, input preprocessing/denoising, ensembles, monitoring confidence, rate-limiting probing, not exposing raw scores, combining ML with rules and human review for high-stakes decisions.

**Q: Model extraction (stealing)?** Attacker queries your API many times and trains a copy.
**Defenses:** rate limits and quotas, detect systematic query patterns, return labels not full probabilities, watermark model outputs, legal terms.

**Q: Membership inference?** Attacker determines whether a specific record was in the training data (a privacy leak, e.g. "this patient was in the cancer dataset").
**Defenses:** regularization (overfit models leak more), differential privacy, limit output detail.

**Q: Model inversion / training data extraction?** Reconstruct training data from the model (LLMs can repeat memorized text like emails or keys).
**Defenses:** deduplicate and scrub PII/secrets from training data, differential privacy, output filters, test for memorization.

**Q: Fraud and abuse adversaries adapt. How is that different?** Attackers change behavior after you deploy (concept drift by design). Use frequent retraining, rules for quick response, red-teaming, and features that are costly for attackers to fake.

## 4. Supply chain security

**Q: Risks?** Downloaded model files can contain **malicious code** (Python pickle files execute code when loaded), compromised open-source packages, poisoned public datasets, third-party model APIs changing behavior, malicious plugins/tool servers.
**Defenses:**
- Prefer safe weight formats (e.g., safetensors) over pickle; never load untrusted pickles.
- Pin versions and hashes of models, datasets and packages; scan dependencies; private mirrors.
- Model and dataset provenance records (who trained, on what, when). People call this an "AI bill of materials".
- Sandboxed evaluation of new third-party models before use.
- Vendor reviews for model providers (data retention, training on your data, regions).

## 5. Defenses checklist

Use this as a closing list in any design interview:
1. **Identity & access:** authN for users, authZ enforced in backend, tenant isolation, least privilege for tools and services.
2. **Data:** minimization, classification (public/internal/confidential/PII), encryption in transit and at rest, retention limits, access logging.
3. **Input controls:** validation, size limits, injection/abuse classifiers, file scanning.
4. **Output controls:** PII/secret filters, policy classifiers, output treated as untrusted in downstream systems.
5. **Action controls:** risk tiers, approvals, limits, idempotency, undo.
6. **Model controls:** safe formats, version pinning, evals for safety, red-teaming before launch.
7. **Monitoring:** abuse patterns, cost spikes, unusual queries (extraction), drift, safety-violation rates, audit logs.
8. **Incident response:** kill switch / feature flag, rollback, credential revocation, user notification process, post-mortem.

## 6. Privacy

**Q: What is PII and how do you handle it in ML pipelines?** Personally identifiable information: names, emails, phone numbers, IDs, addresses, plus quasi-identifiers (ZIP + birth date + gender can identify most people). Handle by: detect (regex + NER models), minimize (don't collect what you don't need), mask/tokenize before training and logging, restrict access, set retention, and keep a data inventory.

**Q: Anonymization vs pseudonymization?** Pseudonymization replaces identifiers with tokens but can be reversed with a key → still personal data under many laws. Anonymization makes re-identification practically impossible. That is hard to achieve, and simple removal of names is usually not enough.

**Q: k-anonymity?** Each record is indistinguishable from at least k−1 others on quasi-identifiers. Weak against attackers with background knowledge; extended by l-diversity and t-closeness.

**Q: Differential privacy (DP)?** A mathematical guarantee that the output (statistic or model) changes very little whether or not any single person's data is included. Achieved by adding calibrated noise. **ε (epsilon)** = privacy budget: smaller ε → stronger privacy, lower accuracy. **DP-SGD** clips per-example gradients and adds noise during training.

**Q: Federated learning?** Train on devices or separate organizations without moving raw data: clients compute updates locally, a server aggregates them (FedAvg). Used for keyboards, hospitals. Challenges: non-IID data across clients, communication cost, updates can still leak information → combine with **secure aggregation** and DP.

**Q: Other privacy-enhancing technologies?** Secure multi-party computation, homomorphic encryption (compute on encrypted data; slow), trusted execution environments (confidential computing), synthetic data (check it doesn't memorize real records).

**Q: Data protection principles you should mention (GDPR-style)?** Lawful basis/consent, purpose limitation (data collected for X not reused for Y without basis), data minimization, storage limitation, accuracy, security, and individual rights: access, correction, deletion ("right to be forgotten"), objection, and rights around **solely automated decisions with significant effects** (explanation and human review).

**Q: Why is the right to be forgotten hard in ML?** Data may be in raw storage, feature store, training snapshots, vector indexes, caches, logs, backups, **and inside trained model weights**. Plan: data lineage to find every copy; delete from stores and indexes; retrain on schedule without the data (or use **machine unlearning** techniques, which are still an active research area); prefer RAG over fine-tuning for personal data so deletion = delete from index.

**Q: Data residency?** Some data must stay in a specific country/region. Design: region-specific deployments and storage, region-pinned model endpoints, no cross-region logging/replication of that data, vendor contracts covering regions.

**Q: What do you check before sending customer data to a third-party LLM API?** Data retention, whether data is used for training, encryption, regions, certifications, contractual terms, zero-retention options; redact PII before sending when possible.

## 7. Fairness

**Q: Where does bias come from?** Historical bias in labels (past decisions were biased), representation bias (group under-sampled), measurement bias (proxy labels like "arrests" for "crime"), aggregation bias (one model for very different groups), deployment bias (used in a different context than designed), feedback loops.

**Q: Fairness metrics?**
| Metric | Meaning |
|---|---|
| **Demographic parity** | same positive-prediction rate across groups |
| **Equal opportunity** | same true positive rate (recall) across groups |
| **Equalized odds** | same TPR **and** FPR across groups |
| **Predictive parity** | same precision across groups |
| **Calibration within groups** | a score of 0.7 means 70% for every group |
| **Individual fairness** | similar individuals get similar outcomes |

**Q: Can you satisfy all of them?** No. When base rates differ between groups, several of these are mathematically incompatible (impossibility results). You must **choose based on context** with stakeholders and document the choice.

**Q: How do you mitigate bias?**
- **Pre-processing:** collect more representative data, reweight/resample, fix biased labels, remove proxy features (carefully: removing the protected attribute alone doesn't remove bias).
- **In-processing:** fairness constraints or adversarial debiasing during training.
- **Post-processing:** group-specific thresholds (check legal acceptability), calibration.
- **Process:** slice-based evaluation before every launch, human review for high-stakes cases, monitoring by group after launch.

**Q: Fairness in LLMs?** Stereotypes in generations, different quality for different languages/dialects, refusing more for some groups. Evaluate with counterfactual prompts (swap names/genders/dialects and compare outputs), red-teaming, per-language eval sets.

## 8. Explainability and transparency

**Q: Global vs local explanations?** Global: how the model behaves overall (feature importance, partial dependence). Local: why this one prediction (SHAP values for this applicant).

**Q: Methods?**
| Method | Notes |
|---|---|
| Interpretable models (linear, small trees, GAMs) | best when regulation requires clear reasons |
| **SHAP** | game-theory based feature attributions; consistent; can be slow; correlated features complicate |
| **LIME** | fits a simple local model around one prediction; unstable |
| Permutation importance | global, model-agnostic |
| Partial dependence / ICE plots | effect of one feature |
| Counterfactual explanations | "If income were $5k higher, the loan would be approved." Users can act on it |
| Grad-CAM / saliency | which image regions mattered |
| Attention visualization | not a reliable explanation by itself |
| LLM citations / reasoning summaries | show sources; reasoning text may not reflect true internal process |

**Q: Model cards and datasheets?** Short documents describing a model's intended use, out-of-scope uses, training data, evaluation results (including by group), limitations, and ethical considerations. Datasheets do the same for datasets. Standard practice for responsible releases.

**Q: Transparency to users?** Tell users when they are interacting with AI, label AI-generated content, give reasons for important automated decisions, and offer a way to reach a human or appeal.

## 9. Regulation and risk tiers

Many AI regulations (for example, the EU's AI Act) use a **risk-based approach**. Described generally:

| Tier | Examples | Typical obligations |
|---|---|---|
| **Unacceptable / prohibited** | manipulative systems exploiting vulnerable people, certain social scoring | not allowed |
| **High risk** | credit scoring, hiring, education access, medical devices, critical infrastructure, law enforcement uses | risk management, data governance, documentation, logging, human oversight, accuracy/robustness, conformity checks |
| **Limited risk / transparency** | chatbots, deepfakes/generated content | tell users it's AI, label generated content |
| **Minimal risk** | spam filters, game AI | voluntary codes |

General-purpose / foundation model providers often have extra duties (technical documentation, copyright policies, and more for very capable models). Sector rules also apply: finance (fair lending, model risk management), health (medical device and health data rules), employment (anti-discrimination). **Interview answer:** identify the risk level of the use case early, and build documentation, logging, human oversight and evaluation into the design from day one.

## 10. AI governance inside a company

- **AI use policy:** which tools/models are approved, what data may be used with them.
- **Model inventory / registry:** every production model with owner, purpose, risk tier, data used, evaluation results.
- **Review process:** risk assessment before launch (privacy, security, fairness, legal); higher risk → more review.
- **Red-teaming:** structured adversarial testing before release and regularly after.
- **Human oversight design:** who can override, how, and are they trained not to rubber-stamp (automation bias).
- **Incident management:** process for AI incidents (harmful output, data leak, biased decisions), with post-mortems.
- **Monitoring and audits:** periodic re-evaluation, especially after model or data changes.
- **Roles:** model owner, data steward, security, legal/privacy, responsible-AI reviewers.

---

## 11. What-if scenarios

### A user tricked the support chatbot into showing another customer's order details (data breach).
**Mitigate now:** disable the affected tool or feature, preserve logs, start the incident process (security plus legal/privacy, since notification duties may apply).
**Causes (ranked):** order-lookup tool trusted an order ID chosen by the model instead of checking the logged-in user; shared cache/memory across users; retrieval without tenant/ACL filters; prompt injection.
**Isolate:** replay the conversation trace; check which tool call returned the data and what authorization it used.
**Fix:** authorization in the backend (tool only returns orders owned by the authenticated user), user-scoped caches/memory, ACL pre-filtering, output PII checks.
**Prevent:** authorization tests ("user A cannot read B"), red-team prompts in CI, audit logs and alerts on cross-account access patterns.

### You discover poisoned data in the training set (spam reviews designed to fool the classifier).
**Isolate:** find the source (one data feed? specific accounts? time window?), measure how much and which model versions trained on it.
**Fix now:** roll back to a model trained before the poisoning, block the source.
**Long-term:** retrain on cleaned data, provenance tracking, anomaly detection on incoming training data, cap influence per user/source, backdoor trigger tests.
**Prevent:** data validation gates in the training pipeline, trusted-source policies.

### A regulator (or customer) asks: "Why was this loan application denied?"
**Answer structure:** the decision record must be reproducible: model version, input features at decision time, score, threshold, and policy rules applied (log all of these). Provide **reason codes** from local explanations (SHAP or an interpretable model), plus counterfactual guidance ("higher income or lower debt ratio would change the outcome"). Show the model's documentation (model card, validation, fairness tests) and the human-review/appeal process.
**If you can't explain it:** that is a design flaw for a high-risk use case → use interpretable models or constrained models, and log decisions properly.

### A user asks you to delete their data, but it was used to fine-tune a model.
**Steps:** delete from raw data, features, vector indexes, caches, logs (per retention policy) using data lineage; for the model: assess risk (was the data memorizable? test by probing), retrain/fine-tune again without the data on the next cycle or sooner if needed, or apply unlearning methods with validation.
**Prevent:** don't fine-tune on personal data unless necessary; prefer RAG for personal facts; record which datasets each model used.

### Your hiring/credit model shows lower approval rates for one group.
**Clarify:** which fairness metric matters here and what is legally required (with legal team). **Isolate:** slice metrics (TPR, FPR, calibration by group), check representation in data, look for proxy features (ZIP code, school), check label bias.
**Fix:** better data, remove/transform proxies, fairness-aware training, threshold review, human review for borderline cases. Pause the model if harm is serious.
**Prevent:** fairness tests as a launch gate, monitoring by group, documentation of trade-offs. See [04 #29](04-what-if-scenarios.md#29-model-is-biased-against-a-user-group).

### Attackers fool your vision model with stickers on products (adversarial attack).
**Fix now:** add rules/human checks for the affected flow, collect the attack examples.
**Long-term:** adversarial training with physical-style augmentations, ensembles of different models, multi-sensor/multi-view checks, confidence monitoring, rate-limit probing.
**Prevent:** red-team the model before launch with known attack types.

### Someone is cloning your model through your public API.
Signs: high-volume, systematic, diverse queries from few accounts. **Fix:** rate limits and quotas, return less detail (labels instead of probabilities), anomaly detection on query patterns, output watermarking, terms of service enforcement.

### An engineer downloaded a community model file and loaded it in production.
Supply-chain risk (pickle files can run code). **Fix now:** check the environment for compromise, rotate credentials if needed. **Long-term:** only safe formats (safetensors), approved model registry, scanning, sandboxed evaluation, pinned hashes.

### The LLM's answers are noticeably worse for users writing in a regional dialect.
Fairness/quality gap. Build per-language/dialect eval sets, counterfactual tests, add representative data or translation steps, choose models that perform better on those languages, monitor quality by language.

### Your team wants to send customer support transcripts to an external LLM provider.
Check data processing terms (retention, training use, regions), redact PII before sending, get privacy/legal approval, data minimization (only needed fields), logging and access controls, option for a self-hosted model for the most sensitive data.
