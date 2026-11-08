# 29 — Senior, Staff & Leadership Rounds (AI/ML)

For senior engineer, staff/principal engineer, tech lead and engineering manager roles in AI/ML.
At this level, interviewers care less about *whether* you can build a model and more about **judgment**: what to build, what not to build, how to reduce risk, and how to get people aligned.

Basic behavioral prep (STAR, project deep dive) is in [15-behavioral-and-project-deep-dive.md](15-behavioral-and-project-deep-dive.md). This chapter builds on it.

### Contents
1. [What changes at senior levels](#1-what-changes-at-senior-levels)
2. [Technical strategy & roadmaps](#2-technical-strategy--roadmaps)
3. [Prioritization & build vs buy](#3-prioritization--build-vs-buy)
4. [Managing ML project risk and uncertainty](#4-managing-ml-project-risk-and-uncertainty)
5. [Estimating ML projects](#5-estimating-ml-projects)
6. [Technical debt in ML systems](#6-technical-debt-in-ml-systems)
7. [Org design for ML teams](#7-org-design-for-ml-teams)
8. [Leading people: influence, mentoring, hiring](#8-leading-people-influence-mentoring-hiring)
9. [Cross-functional communication](#9-cross-functional-communication)
10. [Incidents & postmortems](#10-incidents--postmortems)
11. [Practice questions with model answers](#11-practice-questions-with-model-answers)
12. [What-if leadership scenarios](#12-what-if-leadership-scenarios)

---

## 1. What changes at senior levels
| Level | Scope | Interviewers look for |
|---|---|---|
| Mid-level | A feature / a model | Delivers well-defined work, good technical depth |
| **Senior** | A system or project end to end | Owns ambiguity, makes good trade-offs, mentors others |
| **Staff / Principal** | Multiple teams, a technical area | Sets direction, influences without authority, prevents big mistakes, multiplies others |
| **Tech lead / Manager** | A team | Delivery, people growth, hiring, alignment with business |

**Signals that you are senior:**
- You start from the **business problem**, not the model.
- You talk about **trade-offs, risks, and what you chose *not* to do**.
- Your stories include **other people** (you unblocked, aligned, coached).
- You have **numbers** for impact.
- You admit mistakes and show what changed afterwards.

## 2. Technical strategy & roadmaps
**Q: How do you create a technical strategy for an AI/ML area?**
1. **Understand the goal:** company objectives, user pain points, constraints (data, people, budget, regulation).
2. **Assess today:** current systems, data quality, tooling, skills, tech debt.
3. **Define where to be in 12–24 months:** a few clear bets (e.g., "shared feature store", "LLM gateway for all teams", "evaluation platform").
4. **Path:** phased milestones, each delivering value on its own (no "big bang in 18 months").
5. **Write it down** (1–3 page doc), get feedback early, revise, communicate widely.
6. **Measure:** metrics that show progress (time to deploy a model, % models monitored, cost per prediction).

**Q: What makes a good roadmap?** Outcome-based (problems solved), not a list of features; has explicit priorities and non-goals; reviewed regularly; balances new features, reliability, and tech debt (e.g., 70/20/10).

## 3. Prioritization & build vs buy
**Prioritization frameworks to name:** impact vs effort matrix, RICE (Reach × Impact × Confidence / Effort), cost of delay, "one-way vs two-way door" decisions (reversible decisions → move fast; irreversible → be careful).

**Build vs buy (very common for AI: vector DB, LLM API vs self-host, labeling tools, MLOps platforms):**
| Consider | Questions |
|---|---|
| Core differentiation | Is this our competitive advantage? If not, prefer buy. |
| Total cost | License/API cost vs engineers to build **and maintain** for years |
| Time to value | How soon do we need it? |
| Fit & control | Does the vendor meet requirements (latency, data residency, security)? Lock-in risk? |
| Team skills | Can we operate it at 3 AM? |
| Exit plan | Can we switch later? Use abstraction layers (e.g., an LLM gateway). |

**Model answer pattern:** *"I'd buy (or use managed) for undifferentiated infrastructure and build where it's our core advantage — with an abstraction layer so we can switch later. Then I'd revisit when the scale or cost changes."*

## 4. Managing ML project risk and uncertainty
ML projects are uncertain: you don't know if the data supports the goal until you try.

**Techniques:**
- **Feasibility spike first (1–3 weeks):** baseline + quick data analysis + rough model → go / no-go decision with stakeholders.
- **Define success and "kill criteria" upfront:** "If we can't reach 80% precision at 50% recall by week 6, we stop or change scope."
- **Start with the simplest thing:** rules/heuristics, then classic ML, then deep learning/LLMs.
- **Ship thin end-to-end slice early:** a simple model in production with monitoring beats a perfect model in a notebook.
- **Human-in-the-loop** for early versions to reduce risk.
- **Risk register:** data availability, label quality, latency, compliance, adoption, dependencies.
- **Communicate uncertainty honestly:** ranges and confidence, not single dates.

## 5. Estimating ML projects
- Break into phases: **data (access, cleaning, labels)** → baseline → iteration → productionization → monitoring → launch. Data work is usually **50%+ of the time** — say this.
- Estimate phases separately; give **ranges** (best/likely/worst); re-estimate at milestones.
- Time-box research phases instead of promising results.
- Include non-modeling work: reviews (security, legal, privacy), integration, A/B test duration, documentation, on-call.

## 6. Technical debt in ML systems
Common ML-specific debt (from "Hidden Technical Debt in ML Systems" ideas):
- **Glue code & pipeline jungles** — ad-hoc scripts connecting everything.
- **Entanglement (CACE):** "Changing Anything Changes Everything" — one feature change shifts the whole model.
- **Undeclared consumers:** other teams silently use your model's outputs.
- **Data dependencies** stronger than code dependencies, with no contracts.
- **Dead experimental code paths** and unused features.
- **Feedback loops** — model affects its own training data.
- **Config debt** — thousands of untracked settings, prompts in random places.
- **No monitoring / no evals** — the most dangerous debt.

**How to handle debt as a leader:** make it visible (debt register with cost/risk), tie fixes to business impact ("each deploy takes 2 days → 1 hour saves X"), reserve capacity each quarter, fix debt while building related features, set standards (paved road) to stop new debt.

## 7. Org design for ML teams
| Model | How | Pros | Cons |
|---|---|---|---|
| **Centralized** ML team | One team serves the whole company | Shared standards, strong ML community | Far from product, becomes a bottleneck |
| **Embedded** | ML engineers inside product teams | Close to users and business | Duplicate infrastructure, isolated MLEs |
| **Hub and spoke (hybrid)** | Central **ML platform** team + embedded applied teams | Shared infra + product focus | Needs clear ownership boundaries |

**Platform team rule of thumb:** treat internal teams as customers; build the "paved road" (standard way to train, deploy, monitor, evaluate) that is easier than doing it yourself; measure adoption and time-to-production.

## 8. Leading people: influence, mentoring, hiring
**Leading without authority (staff engineers):** understand others' goals first; use data and prototypes instead of opinions; write proposals (RFC/design docs) and invite critique; find allies; disagree and commit when the decision is made.

**Mentoring:** regular 1:1s; give stretch tasks with safety nets; review design docs, not just code; teach debugging methods (like [03](03-debugging-framework.md)); give credit publicly; give specific, kind, direct feedback.

**Hiring for ML:** define the role clearly (research vs applied vs platform); structured interviews with rubrics; test practical skills (debugging, system design, data sense), not trivia; look for curiosity and engineering rigor; diverse panels; fast, respectful process.

**Performance issues:** clarify expectations, give specific feedback early with examples, agree on a plan with support, follow up, document; escalate if no improvement.

## 9. Cross-functional communication
| Audience | They care about | How to talk |
|---|---|---|
| **Executives** | Business impact, risk, cost, timeline | 1-page summary, decision needed, options with trade-offs, recommendation first |
| **Product managers** | User value, scope, launch dates | What the model can/can't do, confidence ranges, MVP options |
| **Legal / compliance / privacy** | Data use, consent, regulation, liability | Data flows, retention, explainability, human oversight, audit logs |
| **Engineers on other teams** | APIs, dependencies, reliability | Contracts, SLAs, versioning, migration plans |
| **Customers / support** | Why the AI did something | Plain language, limitations, how to give feedback |

**Explaining ML to non-technical people:** use analogies, focus on outcomes and error types ("it will miss about 1 in 20 fraud cases and wrongly block about 1 in 1,000 good customers"), never hide limitations.

## 10. Incidents & postmortems
**During an incident (as leader):** declare it, assign roles (incident commander, communications, investigators), **mitigate first** (rollback, disable feature, fallback), communicate regularly to stakeholders, keep a timeline.
**After:** **blameless postmortem** — what happened, impact, timeline, root causes (often several), what went well, action items with owners and dates, and follow-up until done. Focus on systems and processes, not individuals.
AI-specific incidents: harmful/incorrect outputs at scale, data leakage between users, model drift causing business loss, runaway costs.

---

## 11. Practice questions with model answers

**1. Tell me about the most complex technical decision you made.**
STAR: *Situation:* three teams each built their own LLM integrations; costs and incidents were growing. *Task:* I proposed a shared approach. *Action:* compared options (each team continues / buy a vendor gateway / build a thin internal gateway), wrote an RFC with cost and risk analysis, ran a 2-week prototype with one team, and chose the thin internal gateway with a provider abstraction. *Result:* all teams migrated in a quarter, LLM cost dropped 35% with caching and routing, and provider outages no longer took features down. Lesson: prototype before arguing.

**2. How do you decide whether to use ML at all?**
Ask: is there a clear decision to improve, enough data with labels or feedback, a tolerance for errors, and value above the cost of building and maintaining it? Always build a non-ML baseline first. If rules achieve 90% of the value, ship rules.

**3. How do you balance research exploration and delivery?**
Time-boxed exploration with clear questions and decision points; keep a production baseline improving in parallel; share findings even when negative; portfolio approach (most effort on likely wins, some on bets).

**4. A stakeholder wants 99% accuracy. What do you do?**
Understand why (what decision depends on it, what error type hurts), show the trade-off curve (precision vs recall), propose options: high-confidence automation + human review for the rest; agree on metrics that reflect business cost.

**5. How do you set the technical direction for a team that's new to LLMs?**
Start with use cases with clear value and low risk; create shared foundations (evaluation set, prompt/version management, gateway, guardrails); train the team; set standards (no launch without evals and monitoring); review progress monthly.

**6. Describe a time you disagreed with your manager.**
Show respectful disagreement with data, listening to their constraints, finding a middle ground or disagreeing and committing, and the result. Avoid stories where you were "right and they were dumb".

**7. How do you handle a project that is failing?**
Detect early via milestones and metrics; be honest with stakeholders quickly; diagnose (wrong problem, bad data, unrealistic scope, team issues); options: rescope, pivot, add help, or stop. Stopping a project early is a success if it saves resources — say this.

**8. How do you measure the success of an ML platform team?**
Adoption (teams/models using it), time from idea to production, number of incidents, % models with monitoring and evals, cost per model/prediction, internal user satisfaction.

**9. How do you make sure ML models are fair and safe?**
Define risks early with legal/ethics; slice-based evaluation; red-teaming for LLMs; human oversight for high-stakes decisions; documentation (model cards); monitoring; clear escalation path and authority to stop launches.

**10. How do you grow junior engineers?**
Clear expectations, stretch projects with support, pair on debugging and design, feedback in 1:1s, let them present their work, sponsor them for opportunities.

**11. How do you deal with tech debt when product wants only features?**
Translate debt into business terms (slower delivery, incidents, costs), propose a fixed capacity share, bundle debt fixes into feature work, show results to build trust.

**12. Describe a time you influenced a team you didn't manage.**
Example: convinced another team to adopt data contracts by showing how 4 of the last 6 model incidents came from their schema changes, proposed a lightweight process, offered to build the CI check myself. Result: zero schema-related incidents next quarter.

**13. How do you choose between two strong technical proposals from your team?**
Agree on decision criteria first (cost, risk, time, reversibility); time-boxed prototypes if needed; decide, document the reasoning (ADR), and support the chosen path; give credit to both.

**14. How do you evaluate a vendor's AI product?**
Run it on *our* data with *our* eval set, check latency/cost at our scale, security & data handling (training on our data? retention? region?), SLAs, lock-in and exit plan, references. See [05 #3](05-case-studies.md#3-llm-gateway--internal-llm-platform) for abstraction.

**15. What would you do in your first 90 days as ML tech lead?**
30 days: listen — 1:1s with team and stakeholders, understand systems, data, pain points, metrics. 60 days: pick 1–2 quick wins, write a draft strategy. 90 days: agreed roadmap, team processes (design reviews, eval standards, on-call), first improvements shipped.

**16. How do you handle an underperforming team member?**
See §8: specific feedback early, understand causes (skills, clarity, personal issues), a support plan with clear goals, regular follow-up, fair documentation, escalate with HR if needed.

**17. How do you communicate a delay to executives?**
Early, with the reason, impact, new realistic range, options (cut scope / add people / move date) and your recommendation. Never surprise them at the deadline.

**18. How do you keep ML systems reliable at scale?**
SLOs, monitoring of data/model/system, canary deployments, rollback, runbooks, on-call, postmortems, regular game days, and evals in CI.

**19. Tell me about a mistake that had real impact.**
Own it fully, explain impact with numbers, what you did immediately, what systemic change prevented recurrence, what you learned. (See failure example in [15](15-behavioral-and-project-deep-dive.md#part-b--behavioral-questions-star-method).)

**20. How do you decide build vs buy for a vector database?**
Scale (millions vs billions of vectors), existing stack (Postgres → pgvector is often enough), latency/filtering needs, ops skills, cost, data residency. Start simple, abstract the interface, migrate if limits appear.

**21. How do you prioritize between many AI feature requests?**
Value × confidence / effort, strategic alignment, data readiness, risk; group into themes; say no clearly with reasons; review quarterly.

**22. How do you ensure knowledge isn't stuck in one person?**
Documentation, design docs, pairing, rotating on-call, code reviews by multiple people, runbooks, recorded demos.

**23. What's your approach to design reviews?**
Written doc before code for significant changes; reviewers from affected teams; focus on goals, alternatives, risks, rollout, monitoring; time-boxed; decision recorded.

**24. How do you think about AI regulation and compliance?**
Know the main ideas (risk-based rules like the EU AI Act, privacy laws like GDPR, sector rules in finance/health), involve legal early, build documentation, data lineage, human oversight, and the ability to explain and delete data into the system design from the start.

**25. Why do ML projects fail, in your experience?**
Wrong problem or no clear business owner, data not available or poor quality, success not defined, no path to production, no monitoring after launch, users don't trust or adopt the output. Mention how you prevent each.

**26. How do you build trust with a skeptical business team?**
Start small with a pilot they choose, show results in their metrics, be transparent about failures, involve them in error analysis, deliver consistently.

---

## 12. What-if leadership scenarios
(Same idea as [03](03-debugging-framework.md): clarify → options → decide → communicate → prevent.)

### Your model fails publicly right after launch (bad outputs go viral / big customer complains)
1. **Mitigate first:** rollback or disable the feature, or add a stricter filter; inform stakeholders and support within the hour.
2. **Assess impact:** how many users, what harm, legal/PR risk.
3. **Communicate:** honest internal update, help comms team with external message.
4. **Root cause** via postmortem (eval gaps? launch too fast? missing guardrails?).
5. **Prevent:** stronger launch checklist (red-teaming, slice evals, staged rollout, kill switch).

### Your team strongly disagrees on the approach (fine-tune vs RAG, PyTorch vs JAX, build vs buy)
Make the disagreement productive: agree on criteria, let each side write a short proposal, run a time-boxed experiment on the same eval set, decide (or escalate with a clear recommendation), document the decision, and ask everyone to commit. Thank the "losing" side — their concerns become risks to monitor.

### An executive says "Put GenAI in every product this quarter"
Don't say no; channel the energy: list candidate use cases, score by value, feasibility, and risk, pick 2–3 high-value pilots with clear metrics, build shared foundations (gateway, evals, guardrails) to make later launches cheap and safe, report results honestly. Explain risks (cost, hallucinations, data privacy) in business terms.

### The deadline is impossible
Clarify what's truly fixed (date? scope? quality?). Offer options: reduced scope (MVP), phased launch, more people (with ramp-up cost), or a new date. Give your recommendation with confidence ranges. Don't silently burn the team out or cut evaluation and safety.

### Your key engineer resigns in the middle of a critical project
Short-term: knowledge transfer plan for the notice period (docs, recorded walkthroughs, pairing), reassign ownership, re-plan timeline with stakeholders. Long-term: reduce bus factor (see Q22), understand why they left (stay interviews with others), backfill hiring.

### An engineer raises an ethical concern about a model (bias, privacy, misuse)
Take it seriously and thank them — psychological safety matters. Pause launch if the risk is real; investigate with data (slice metrics, privacy review); involve legal/ethics/responsible-AI team; decide transparently and document; fix or stop. Never punish the person who raised it.

### Product wants to launch, but evaluations show the model isn't ready
Show the evidence in business terms (error rate, affected users, risk), propose alternatives (limited beta, human review, narrower scope, feature flag with staged rollout), agree on launch criteria together. If overruled, document the risk and ensure monitoring + kill switch.

### Two teams built overlapping ML platforms
Map both (users, features, costs), meet both leads, agree on a target architecture and a migration path, avoid "winner and loser" framing — merge the best parts, set timeline and ownership.

### Your team's model costs more to run than the revenue it creates
Measure unit economics (cost per prediction vs value), then: optimize (smaller models, caching, batching, routing), reprice or limit usage, or retire the feature. Present options with numbers to leadership.

### A regulator or big customer asks "how does your AI make decisions?"
Provide documentation you should already have: model cards, data sources and lineage, evaluation results by segment, human oversight process, explanation methods, incident history and controls. If you don't have them — that's a priority action item.
