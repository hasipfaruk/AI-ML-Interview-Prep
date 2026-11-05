# 15 — Behavioral & Project Deep-Dive Round

For ML/AI roles, **"Tell me about a project you built"** is often the round that decides the offer.
Interviewers dig 5–6 levels deep with "why?" and "what if?". If you can't explain *your own* decisions, it looks like you didn't make them.

---

## Part A — The project deep dive

### Prepare 2–3 projects using this template (write it down!)

| Section | Your notes |
|---|---|
| **1. Problem & business goal** | What problem, for whom, why it mattered, how success was measured (business metric) |
| **2. Your role** | What *you* did vs. the team. Use "I". |
| **3. Data** | Source, size, labels (how obtained, quality), splits, imbalance, leakage risks you handled |
| **4. Baseline** | What simple approach did you compare against? Its score? |
| **5. Approach** | Model/architecture and **why this one over alternatives** |
| **6. Evaluation** | Offline metrics (why these?), validation strategy, error analysis findings |
| **7. Deployment** | How served (batch/real-time), latency, infra, monitoring |
| **8. Results / impact** | Numbers: "+12% recall at same precision", "cut cost 40%", "saved 20 hrs/week" |
| **9. Challenges** | The hardest problem and how you debugged it (use C.L.H.I.F.P. from [03](03-debugging-framework.md)) |
| **10. Trade-offs** | What you sacrificed and why |
| **11. What you'd do differently** | Shows maturity |
| **12. Next steps** | How you'd improve with more time/data |

### Questions you WILL be asked — prepare an answer for each

**Data**
- How much data? How was it labeled? How did you check label quality?
- Was it imbalanced? How did you handle it?
- How did you split the data? Could there be leakage?
- What features mattered most? Any surprising ones?

**Model**
- Why this model? What else did you try? Why not a simpler/bigger one?
- What hyperparameters mattered? How did you tune them?
- Why this loss/metric?

**Evaluation**
- How do you know it actually works? Offline vs online results?
- Where does it fail? (error analysis — always have 2–3 failure categories ready)
- Did you compare against a baseline?

**Production**
- How is it served? Latency? Cost?
- How do you monitor it? What happens when it degrades?
- How often retrained?

**What-ifs (this is where people fail — practice!)**
- What if the data doubled / was 100× bigger?
- What if labels were unavailable?
- What if latency had to be 10× lower?
- What if the data distribution changed?
- What if you had to explain predictions to a regulator?
- What if a user group gets worse results?
- (For RAG/LLM projects:) what if answers are inconsistent / hallucinated / slow / expensive? → [04](04-what-if-scenarios.md)

**Golden rule:** if you don't know, say *"We didn't measure that, but here's how I would check it: …"* — that still scores well. Never invent numbers.

### Example (RAG project) — 2-minute pitch
> "I built an internal Q&A assistant over 50k HR and IT documents for ~5,000 employees. The goal was reducing support tickets.
> I owned the retrieval pipeline and evaluation. Baseline was keyword search, which answered ~40% of a labeled set of 300 real questions.
> I used structure-aware chunking with section headers, hybrid BM25 + embedding search, and a cross-encoder reranker. Recall@5 went from 58% to 86%.
> For generation we used temperature 0 with mandatory citations and an 'I don't know' path when retrieval scores were low; faithfulness on our eval set was 94%.
> The hardest problem was inconsistent answers — we traced it to duplicate policy versions in the corpus and fixed it with effective-date metadata and dedupe.
> After launch, IT tickets for covered topics dropped 25%. If I did it again, I'd build the eval set on day one instead of week four."

That pitch answers 10 follow-ups before they're asked.

---

## Part B — Behavioral questions (STAR method)

**STAR:** **S**ituation (1 line) → **T**ask (your responsibility) → **A**ction (what *you* did — 60% of the answer) → **R**esult (numbers + what you learned).

### Prepare 6–8 stories that cover these
| Theme | Typical question |
|---|---|
| Conflict | Tell me about a disagreement with a teammate/manager. |
| Failure | Tell me about a project that failed / a mistake you made. |
| Ambiguity | A time requirements were unclear. |
| Ownership | A time you went beyond your role. |
| Influence | Convincing others without authority (e.g., "use a simpler model"). |
| Deadline / pressure | Delivering under a tight timeline; what you cut. |
| Learning | Learning a new technology quickly. |
| Impact | Your most impactful work. |
| Stakeholders | Explaining ML to non-technical people. |
| Ethics / quality | Pushing back on shipping a model that wasn't ready. |

One story can cover several themes — map each story to 2–3 themes.

### Good vs weak answer — "Tell me about a failure"
- ❌ "I'm a perfectionist…" / blaming others / no lesson.
- ✅ "I shipped a churn model without slice-level evaluation. Two weeks later sales noticed it flagged nearly all new customers — a feature was missing for accounts < 30 days old. I rolled back, added a default-handling fix and slice tests to our pipeline. Since then I always evaluate by segment before launch. The relaunched model hit its target."

### Questions to ask the interviewer (always have 2–3)
- What does success look like in this role in the first 6 months?
- How do models/LLM features get from prototype to production here? How do you evaluate them?
- What's the biggest technical challenge the team is facing right now?

---

## Part C — Communication habits that change outcomes
- **Think out loud.** Silence = interviewer can't give you credit.
- **Structure first:** "I'll cover three things: data, model, and deployment."
- **Numbers over adjectives:** "p95 latency 400 ms" beats "pretty fast".
- **Admit unknowns, then reason:** "I haven't used X, but I'd expect it to behave like Y because…"
- **Check in:** "Does this level of detail make sense, or should I go deeper on retrieval?"
- **Simple English is fine.** Clear beats fancy. Short sentences.
