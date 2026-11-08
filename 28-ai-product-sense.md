# 28. AI Product Sense

Senior AI/ML roles, AI product manager roles and many startup interviews include questions like
**"How would you measure success of this AI feature?"** or **"Should we build our own LLM?"**
They test whether you can connect models to **users, business value and cost**, not just accuracy.

### Contents
1. [The product-sense framework](#1-the-product-sense-framework)
2. [Framing a business problem as ML](#2-framing-a-business-problem-as-ml)
3. [Do we even need ML or an LLM?](#3-do-we-even-need-ml-or-an-llm)
4. [Success metrics: north star and guardrails](#4-success-metrics-north-star-and-guardrails)
5. [Build vs buy](#5-build-vs-buy)
6. [MVP and iteration](#6-mvp-and-iteration)
7. [Cost and ROI estimation for AI features](#7-cost-and-roi-estimation-for-ai-features)
8. [UX for AI features](#8-ux-for-ai-features)
9. [Launch and rollout](#9-launch-and-rollout)
10. [Stakeholder communication](#10-stakeholder-communication)
11. [Prioritization](#11-prioritization)
12. [Practice questions with model answers](#12-practice-questions-with-model-answers)
13. [What-if scenarios (product)](#13-what-if-scenarios-product)

---

## 1. The product-sense framework

Use this order for any open product question. Memory trick: **"U-P-S-M-R"** (Users, Problem, Solution, Metrics, Risks).

| Step | What to say |
|---|---|
| **1. Users** | Who uses it? Segments (new vs power users, consumers vs businesses). What do they need? |
| **2. Problem** | What pain are we solving? How do we know it's real (data, complaints, research)? How big is it? |
| **3. Solution** | Options (non-AI first, then AI). Pick one with reasons. Define the MVP. |
| **4. Metrics** | North-star metric, supporting metrics, guardrail metrics. How we'd test it (A/B). |
| **5. Risks** | Quality failures, safety, privacy, cost, trust. Mitigation for each. |

**A sentence you can reuse:**
> "I'd start from the user problem, not the model. The model is only useful if it changes a user outcome we can measure."

---

## 2. Framing a business problem as ML

| Business goal | Possible ML framing | Label / signal |
|---|---|---|
| Reduce customer churn | Classify who will churn; better: **uplift** (who will stay because of an offer) | Churned within 60 days; response to offer |
| Reduce support costs | Classify & route tickets; auto-answer FAQs with RAG | Resolution without human, CSAT |
| Increase sales | Recommend products; rank search results | Purchases, add-to-cart |
| Reduce fraud losses | Score transactions | Chargebacks, confirmed fraud |
| Save employee time | Summarize, draft, extract | Time per task, edit distance of AI draft vs final |

**Questions to ask while framing:**
- What **decision** will the prediction drive? (A prediction no one acts on has zero value.)
- What is the **proxy** we optimize, and how could it diverge from the real goal? (Clicks vs satisfaction.)
- What **error is more costly**: false positive or false negative?
- Where do **labels** come from, and how delayed are they?
- What's the **baseline** today (manual process, rules, nothing)?

---

## 3. Do we even need ML or an LLM?

Strong candidates are willing to say "no ML needed". Use this check:

| Use plain software / rules when… | Use classic ML when… | Use an LLM when… |
|---|---|---|
| Logic is clear and stable | Patterns are complex but the task is narrow (score, classify, rank) | Input or output is open-ended language, images, or code |
| Errors are not acceptable and rules can guarantee correctness | You have labeled data or behavior logs | You need flexibility across many tasks with little labeled data |
| Small volume, a human can do it | Low latency and low cost per prediction matter | Reasoning over text, summarizing, drafting, conversation |
| Example: tax calculation | Example: fraud score, demand forecast | Example: support assistant, document Q&A |

**Rule of thumb:** "Start with the simplest thing that could work, measure it, then add complexity only where the data shows a gap."

---

## 4. Success metrics: north star and guardrails

| Metric type | Meaning | Example (AI support assistant) |
|---|---|---|
| **North star** | The one metric that shows real user/business value | % of tickets resolved without a human, with good CSAT |
| **Supporting / driver** | Explains why the north star moves | Answer acceptance rate, deflection rate, time to answer |
| **Model quality** | Offline and online quality of the AI | Faithfulness, retrieval recall@k, thumbs-up rate |
| **Guardrails** | Must NOT get worse | CSAT, escalation complaints, wrong refunds, latency, cost per ticket, safety incidents |
| **Adoption** | Are people using it? | Weekly active users of the feature, repeat usage |

**Common traps to mention:**
- **Usage ≠ value:** many people trying the feature once is not success; look at retention of the feature.
- **Proxy gaming:** optimizing "answers given" can increase confident wrong answers.
- **Survivorship:** only happy users give feedback; sample conversations for human review.
- **Novelty effect:** usage spikes then drops; measure over weeks.

---

## 5. Build vs buy

| Option | Pros | Cons | Choose when |
|---|---|---|---|
| **Use an API model (buy)** | Best quality, fast to launch, no infra | Per-token cost, vendor dependency, data leaves your system (check contract), rate limits | Most new AI features; validating demand |
| **Open-weight model, self-hosted** | Control, data stays inside, cost-efficient at high volume, can fine-tune | GPU operations, scaling, lower top quality, team skills needed | High volume, strict privacy, narrow task, latency needs |
| **Fine-tune (API or open)** | Better for specific format/style/domain, smaller cheaper model | Needs good data, maintenance, evals | Prompting + RAG not enough, or cost reduction at scale |
| **Train your own foundation model** | Full control | Extremely expensive (millions+), slow, needs rare expertise | Almost never; only if the model *is* the product and you have unique data & budget |
| **Buy a full SaaS product** | Fastest | Least customization, shared roadmap | Commodity need (e.g., meeting transcription) |

**Decision factors to list:** quality needed, data privacy, volume & cost curve, latency, time to market, team skills, strategic differentiation ("is this our core advantage?").

---

## 6. MVP and iteration

1. **Wizard of Oz / manual first:** humans do the task behind the scenes to test if users want it.
2. **Prompt + API prototype** in days; test with internal users.
3. **Eval set** from real examples before scaling (50-200 cases is enough to start).
4. **Limited beta** with clear scope ("only answers HR policy questions").
5. **Measure, collect failures, improve** (prompt → retrieval → model choice → fine-tune, in that order).
6. **Expand scope** gradually.

**Scope cuts that make a good MVP:** one user segment, one language, one task, human-in-the-loop instead of full automation, read-only actions before write actions.

---

## 7. Cost and ROI estimation for AI features

### Token cost math (practice this, interviewers love it)
```
cost per request = (input_tokens × input_price + output_tokens × output_price) / 1,000,000
monthly cost     = cost per request × requests per day × 30
```
**Example:** support assistant, 20,000 conversations/day, 4 turns each.
- Per turn: 3,000 input tokens (system prompt + retrieved context + history), 300 output tokens.
- Assume price: $3 per 1M input tokens, $15 per 1M output tokens (use the real prices of the model you'd pick).
- Per turn: 3,000 × 3/1M + 300 × 15/1M = $0.009 + $0.0045 = **$0.0135**
- Per day: 20,000 × 4 × $0.0135 = **$1,080** → about **$32,400 / month**.

**ROI:** if each conversation resolved by AI saves a $4 human ticket and 40% are resolved:
20,000 × 0.4 × $4 × 30 = **$960,000 / month saved** vs ~$32k LLM cost (+ infra, people). Clear win.

### Levers to cut cost (say these after the math)
| Lever | Typical effect |
|---|---|
| Shorter context (better retrieval, fewer chunks, summarize history) | Input tokens down 30-60% |
| Prompt / prefix caching for the fixed system prompt | Big discount on repeated tokens |
| Model routing (small model for easy questions) | 50-80% cost cut on routed traffic |
| Semantic cache for repeated questions | Removes some calls fully |
| Limit output length | Output tokens are the most expensive |
| Batch API for non-urgent work | Often ~50% cheaper |
| Self-hosting at very high volume | Lower marginal cost, higher fixed cost |

Also count **hidden costs**: embeddings, vector DB, evaluation runs (LLM judges cost tokens too), human review, engineering time.

---

## 8. UX for AI features

AI is probabilistic, so the product must handle being wrong gracefully.

| Principle | How |
|---|---|
| **Set expectations** | Say what it can and can't do; examples of good questions |
| **Show sources** | Citations / links so users can verify |
| **Show confidence carefully** | Use "I'm not sure, here's what I found" or route to human; avoid fake precise percentages |
| **Easy correction** | Edit, regenerate, thumbs down with reason |
| **Human handoff** | One click to a human, with conversation context passed along |
| **Fallbacks** | When the model fails or times out: cached answer, search results, or clear error |
| **Keep humans in control of risky actions** | Preview + confirm before sending emails, payments, deletions |
| **Latency perception** | Stream tokens, show progress steps ("Searching documents…") |
| **Privacy transparency** | Tell users what data is used and stored |
| **Consistency** | Same question should get the same core answer (see [03](03-debugging-framework.md)) |

---

## 9. Launch and rollout

1. **Offline evals pass** (quality, safety, latency, cost thresholds).
2. **Internal dogfooding** → collect failures.
3. **Shadow mode** where possible (AI suggests, human decides, compare).
4. **Staged rollout:** 1% → 10% → 50% → 100% with an A/B test and guardrail alerts.
5. **Kill switch / feature flag** ready.
6. **Monitoring dashboard:** quality (thumbs, escalations), safety incidents, latency, cost per request.
7. **Feedback loop:** weekly review of failures → eval set grows → improvements.

See also [02 §5](02-ml-and-llm-systems.md#5-deployment--experimentation) and [13](13-mlops.md).

---

## 10. Stakeholder communication

| Audience | They care about | How to talk |
|---|---|---|
| Executives | Business impact, risk, cost, timeline | "This reduces support cost ~30%, costs ~$30k/month, main risk is wrong answers, mitigated by citations and human handoff." |
| Product managers | User value, scope, trade-offs | Options with pros/cons, what the MVP includes |
| Legal / compliance | Data use, regulation, liability | Data flow diagram, retention, vendor terms, audit logs |
| Engineers | Architecture, effort, dependencies | Design docs, APIs, SLAs |
| End users | "Can I trust it?" | Clear UI, sources, limits, how to get a human |

**Explaining model uncertainty to non-technical people:**
> "The model is right about 9 times out of 10 on our test questions. For the 1 in 10 it gets wrong, we show sources so people can check, and we send risky cases to a human."

---

## 11. Prioritization

Use **impact × confidence ÷ effort** (ICE/RICE) and add AI-specific factors:
- **Data readiness:** do we already have the data and labels?
- **Error tolerance:** can the use case survive mistakes? (Drafting emails: yes. Medical dosing: no.)
- **Feedback loop:** will usage generate data to improve it?
- **Cost at scale:** is unit economics positive?

**Good first AI use cases:** high volume, repetitive, tolerant of errors with human review, clear success metric (e.g., ticket triage, document extraction, internal search).

---

## 12. Practice questions with model answers

### 1. How would you measure success of an AI writing assistant (like in an email or docs product)?
Users: people writing emails/documents. North star: **% of AI suggestions kept** (accepted with little editing) by weekly active users, or time saved per document. Supporting: suggestion acceptance rate, edit distance between AI draft and final text, repeat usage (D7/D30 retention of the feature). Quality: human ratings on samples, tone/grammar eval. Guardrails: complaints, harmful/off-tone outputs, latency (suggestions must be fast), cost per active user, no drop in overall product retention. Test: A/B test feature on vs off, measure time-to-send and satisfaction.

### 2. Should we build our own LLM?
Almost always no for the base model. Ask: Is the model our core product? Do we have unique data at huge scale and millions in budget? Usually better: API model + RAG + prompt engineering, then fine-tune an open model if cost, privacy or latency demand it. I'd list decision factors (quality, privacy, cost at volume, latency, skills, strategic value) and propose: start with API, build eval set, re-evaluate at a cost/volume threshold.

### 3. Our AI feature has low adoption. Why, and what would you do?
Clarify: low discovery (users don't see it), low trial (they see but don't try), or low retention (try once, don't return)? Look at the **funnel**. Causes: hidden entry point, unclear value, bad first experience (wrong answer), too slow, users don't trust it, doesn't fit workflow. Actions: interview users and read sampled sessions, fix the first-run experience, show example prompts, integrate into existing workflow (suggest, don't make them ask), measure each funnel step after changes.

### 4. How would you decide between a rules-based system and ML for fraud?
Use both: rules for known patterns and hard policies (fast, explainable), ML for complex patterns and ranking risk. Compare on precision/recall at the business cost, maintenance effort, adaptability to new fraud, and explainability. Start with rules if no labels, add ML once chargeback labels accumulate.

### 5. A PM wants to add a chatbot to the app "because everyone has one". How do you respond?
Ask what user problem it solves and what success looks like. Check support logs and search queries for real needs. If the need is narrow (track order), a button may beat a chatbot. If needs are varied and language-heavy, a scoped assistant can help. Propose a small experiment with a clear metric before a big build.

### 6. How do you estimate the cost of an LLM feature before building it?
Estimate requests/day × tokens in/out × price (see [§7](#7-cost-and-roi-estimation-for-ai-features)), add embeddings, vector DB, eval and review costs. Compare with value created per request. Identify cost levers and the break-even point for self-hosting.

### 7. How would you improve a recommendation feature whose clicks are high but users say it's "repetitive"?
Clicks are a weak proxy. Add diversity/novelty constraints, measure long-term retention and satisfaction surveys, penalize near-duplicates, explore new items. Guardrail: don't let CTR drop too much while increasing diversity.

### 8. What metrics would you use for an AI customer support agent?
North star: resolution rate without human **and** CSAT ≥ human baseline. Drivers: deflection rate, first-contact resolution, time to resolve. Quality: correctness on audits, policy compliance, hallucination rate. Guardrails: escalation complaints, wrong actions (refunds), latency, cost per resolved ticket, repeat contacts within 7 days (a sign it didn't really solve the problem).

### 9. Leadership wants 100% accuracy before launch. How do you handle it?
Explain that probabilistic systems are never 100%, and that humans aren't either. Compare with the **current baseline** (human error rate, current process). Agree on an acceptable error rate per error type, and design for mistakes: human review for high-risk cases, citations, easy correction, monitoring. Propose a staged launch on low-risk scope.

### 10. How would you prioritize between improving model accuracy by 2% and reducing latency by 50%?
Depends on what limits user value. Check data: does latency hurt usage (drop-off while waiting)? Do errors cause complaints or escalations? Run small experiments if possible. Often latency wins for interactive features; accuracy wins for high-stakes decisions.

### 11. How do you know if users trust the AI feature?
Behavioral signals: acceptance without edits, users verifying sources less over time (but not blindly), repeat usage, handoff rate, override rate. Surveys. Watch for **over-trust** too (users accept wrong answers) in high-risk domains, and audit samples.

### 12. Design the metric dashboard for a new AI search feature.
Top: north star (successful sessions: click/answer accepted without reformulation). Funnel: queries → results/answers shown → clicks/accepts → task done. Quality: thumbs, no-answer rate, citation click rate, human-rated relevance sample. System: p50/p95 latency, error rate, cost per query. Guardrails: complaints, safety flags. Slice by user segment, language, query type.

### 13. How would you price an AI feature?
Understand cost per use and value per use. Options: included in plan (drives retention), add-on subscription, usage-based (credits). Protect margins with limits for heavy users. Test willingness to pay; watch cost of power users (the top 5% can drive most cost).

### 14. When would you choose a smaller, cheaper model over the best model?
When the task is narrow (classification, extraction), latency matters, volume is high, and evals show the small model meets the quality bar. Use routing: small model by default, escalate hard cases to the big model.

### 15. How would you run an experiment for an LLM feature?
Randomize by user; primary metric tied to value (task completion, retention); guardrails (cost, latency, complaints); enough duration to pass novelty; log model/prompt versions; segment results; check for sample ratio mismatch. See [11](11-statistics-and-ab-testing.md#4-ab-testing).

### 16. An exec asks: "Why can't the AI just do the whole job instead of assisting?"
Explain the error rate and the cost of errors in that job. Show a maturity path: suggest → draft for approval → automate low-risk cases → expand automation as measured accuracy and trust grow.

### 17. How would you choose the first AI use case for a company new to AI?
High volume, repetitive, measurable, low risk if wrong, data available, a motivated business owner. Examples: internal knowledge search, ticket triage, document extraction. Avoid starting with high-stakes autonomous decisions.

---

## 13. What-if scenarios (product)

### Usage of the AI feature spiked at launch, then dropped 70% after 3 weeks.
Novelty effect, or first experiences were disappointing. Isolate: retention cohorts, satisfaction of returning vs churned users, sample their sessions. Fix: improve quality on top use cases, make value obvious in workflow, remove friction (speed). Prevent: judge launch success on 4-8 week retention, not week 1.

### AI cost is growing faster than revenue.
Find the cost per active user and the top 5% heaviest users; break down tokens by feature. Fix now: limits for heavy usage, caching, shorter contexts. Long-term: model routing, smaller fine-tuned model, pricing tiers aligned with usage.

### Users say the AI is "confidently wrong" and complaints are going viral on social media.
Mitigate now: narrow the scope, add disclaimers and citations, route sensitive topics to humans, fix the shared examples. Root cause: hallucination or retrieval failures (see [04 #3](04-what-if-scenarios.md#3-rag-gives-confident-wrong-answers-hallucinations)). Prevent: red-team before launch, eval set of sensitive/edge questions, monitoring social and support channels.

### A big customer refuses to use the AI because of data privacy.
Offer: no training on their data, data retention controls, region/tenant isolation, private deployment or bring-your-own-key, audit logs, clear documentation of data flow. Legal + security review.

### The A/B test shows the AI feature improves engagement but reduces revenue.
Maybe users find answers without buying, or the AI displaces ads/upsells. Analyze segments and funnel; decide with leadership which goal matters; redesign so AI helps toward purchase (product suggestions) while keeping user value.

### The model vendor raises prices 3× or deprecates the model you use.
Keep an abstraction layer (LLM gateway), maintain evals so you can switch models in days, have a second provider tested, consider open-weight models for core tasks.

### Two teams want the same GPUs/budget for different AI projects.
Compare expected impact, confidence, cost and strategic value with numbers; consider shared platform investments (gateway, eval tooling) that help both; escalate with a clear recommendation, not just the conflict.
