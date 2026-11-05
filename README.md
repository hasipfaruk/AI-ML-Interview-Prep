# AI / ML / DL / NLP Interview Prep — Zero to Hero

A complete prep course for **AI Engineer, ML Engineer, Applied Scientist, Data Scientist, NLP / CV / LLM Engineer** interviews.

📄 **Prefer one file?** Download the full course as a PDF: [AI-ML-Interview-Prep.pdf](AI-ML-Interview-Prep.pdf)

Most candidates don't fail because they lack knowledge. They fail because when the interviewer says
**"What if this happens?"** they have no *structured way to think out loud*. Every file here includes those scenario questions with model answers.

---

## Step 1 — Know which rounds you'll face

| Interview round | What they test | Study file(s) |
|---|---|---|
| **ML theory / fundamentals** | bias-variance, metrics, algorithms, overfitting, imbalance | [07-ml-fundamentals.md](07-ml-fundamentals.md) |
| **Deep learning** | backprop, optimizers, CNN/RNN/Transformers, training debugging | [08-deep-learning.md](08-deep-learning.md) |
| **NLP / LLM** | tokenization, embeddings, BERT/GPT, RLHF, LoRA, prompting, hallucination | [09-nlp-and-llms.md](09-nlp-and-llms.md) |
| **Computer vision** | detection, segmentation, ViT, CLIP, mAP, edge deployment | [10-computer-vision.md](10-computer-vision.md) |
| **Statistics & A/B testing** | probability, Bayes, p-values, experiment design | [11-statistics-and-ab-testing.md](11-statistics-and-ab-testing.md) |
| **ML coding** | implement algorithms from scratch (NumPy/PyTorch) | [12-ml-coding.md](12-ml-coding.md) |
| **DSA coding** | LeetCode-style problems | [14-dsa-coding-round.md](14-dsa-coding-round.md) |
| **ML / LLM system design** | design RAG, recommender, fraud system, LLM platform | [01](01-fundamentals.md), [02](02-ml-and-llm-systems.md), [05](05-case-studies.md) |
| **"What if X happens?" / debugging** | production failures, inconsistent outputs, drift, outages | [03](03-debugging-framework.md) (method) + [04](04-what-if-scenarios.md) (50 scenarios) + "what-if" sections in 07–13 |
| **MLOps / production** | CI/CD for ML, serving, monitoring, versioning | [13-mlops.md](13-mlops.md) |
| **Project deep dive & behavioral** | your own projects, STAR stories | [15-behavioral-and-project-deep-dive.md](15-behavioral-and-project-deep-dive.md) |
| **Interview day strategy** | 45-min script, phrases, cheat sheet | [06-interview-playbook.md](06-interview-playbook.md) |

---

## Step 2 — Learn the one method for all "what if" questions

> **C**larify → **L**ayer map → **H**ypotheses (ranked) → **I**solate (how to prove it) → **F**ix (now + long-term) → **P**revent (monitoring/evals)

Read [03-debugging-framework.md](03-debugging-framework.md) **first**. It works for RAG, ML models, training bugs, data pipelines, and infrastructure.

---

## Step 3 — Follow a plan

### 10-week full plan (from zero)
| Week | Theory (1–1.5 h/day) | Practice (1 h/day) |
|---|---|---|
| 1 | 07 ML fundamentals | 14 DSA patterns 1–2 |
| 2 | 11 Statistics + 07 what-ifs | 12 ML coding §1–5 |
| 3 | 08 Deep learning | 14 DSA patterns 3–5 |
| 4 | 09 NLP & LLMs | 12 ML coding §6–12 |
| 5 | 10 Computer vision (skip if not CV role) + 03 framework | 14 DSA patterns 6–9 |
| 6 | 01 System design fundamentals | 04 scenarios A–B (out loud) |
| 7 | 02 ML & LLM systems + 13 MLOps | 04 scenarios C–F |
| 8 | 05 Case studies 1–4 | 14 DSA patterns 10–12 |
| 9 | 05 Case studies 5–11 + 15 project prep | 2 full mock interviews |
| 10 | 06 playbook, revise weak areas | 4 mock interviews (mixed rounds) |

### 2-week emergency plan (interview soon)
| Days | Focus |
|---|---|
| 1–2 | 03 framework + 04 scenarios (your domain sections) |
| 3–4 | 07 + 08 Q&A (read questions, answer out loud) |
| 5–6 | 09 (or 10 for CV) + 11 |
| 7–8 | 02 + 05 case studies 1, 4, 5 |
| 9–10 | 12 ML coding (top 6) + DSA patterns 1, 3, 7 |
| 11–12 | 15 — write 2 project deep dives + 6 STAR stories |
| 13–14 | Mocks + 06 cheat sheet |

### By role — what to prioritize
| Role | Highest priority files |
|---|---|
| **AI / LLM Engineer** | 03, 04, 02, 09, 05, 13, 15 |
| **ML Engineer** | 07, 08, 12, 13, 02, 04, 05, 14 |
| **Data Scientist / Applied Scientist** | 07, 11, 12, 08, 15, 05 (#4–5) |
| **NLP Engineer** | 09, 08, 12, 04 (A–B), 02 |
| **CV Engineer** | 10, 08, 12, 13, 05 (#7–8) |
| **MLOps Engineer** | 13, 02, 01, 04 (C–E), 05 (#3) |

---

## Step 4 — Practice the right way
1. **Say answers out loud.** Reading feels like learning; interviews test speaking.
2. Cover the answer → answer in 60 s (theory) or 3 min (scenario) → compare → mark misses → redo in 2 days.
3. Record mock interviews and watch them back.
4. Ask an AI or a friend to play interviewer: *"Ask me [ML theory / LLM system design / what-if] questions one by one, push back with follow-ups, then score my answer for structure, depth, and trade-offs."*

## All files
| # | File |
|---|---|
| 01 | [System design fundamentals](01-fundamentals.md) |
| 02 | [ML & LLM systems](02-ml-and-llm-systems.md) |
| 03 | [Debugging framework (what-if method)](03-debugging-framework.md) |
| 04 | [50 what-if scenarios](04-what-if-scenarios.md) |
| 05 | [Case studies](05-case-studies.md) |
| 06 | [Interview playbook & cheat sheet](06-interview-playbook.md) |
| 07 | [ML fundamentals](07-ml-fundamentals.md) |
| 08 | [Deep learning](08-deep-learning.md) |
| 09 | [NLP & LLMs](09-nlp-and-llms.md) |
| 10 | [Computer vision](10-computer-vision.md) |
| 11 | [Statistics & A/B testing](11-statistics-and-ab-testing.md) |
| 12 | [ML coding from scratch](12-ml-coding.md) |
| 13 | [MLOps](13-mlops.md) |
| 14 | [DSA coding round](14-dsa-coding-round.md) |
| 15 | [Behavioral & project deep dive](15-behavioral-and-project-deep-dive.md) |

---

## Rebuild the PDF
```bash
pip install markdown pygments
python scripts/build_pdf.py      # needs Chrome or Edge installed
```

## Contributing
Found a mistake, or want to add a scenario question you were asked in a real interview? Open an issue or a pull request.
New "what if" scenarios should follow the same format: **causes (ranked) → how to isolate → fix (now / long-term) → prevent.**

If this helped you, give the repo a ⭐ so others can find it.

## License
Content is licensed under [CC BY 4.0](LICENSE): free to share and adapt, with credit.
