# AI / ML / DL / NLP Interview Prep: Zero to Hero

A complete prep course for **AI Engineer, ML Engineer, Applied Scientist, Data Scientist, NLP / CV / LLM / Speech / RL Engineer, MLOps, Data Engineer and Backend/Software Engineer** interviews, in **every industry** (healthcare, finance, e-commerce, ads, autonomous driving, manufacturing, and 14 more).

**Prefer one file?** Download the full course as a PDF: [AI-ML-Interview-Prep.pdf](AI-ML-Interview-Prep.pdf)

Most candidates don't fail because they lack knowledge. They fail because when the interviewer says
**"What if this happens?"** they have no *structured way to think out loud*. Every file here includes those scenario questions with model answers.

---

## Step 1: Know which rounds you'll face

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
| **"What if X happens?" / debugging** | production failures, inconsistent outputs, drift, outages | [03](03-debugging-framework.md) (method) + [04](04-what-if-scenarios.md) (50 scenarios) + "what-if" sections in 07-13 |
| **MLOps / production** | CI/CD for ML, serving, monitoring, versioning | [13-mlops.md](13-mlops.md) |
| **Project deep dive & behavioral** | your own projects, STAR stories | [15-behavioral-and-project-deep-dive.md](15-behavioral-and-project-deep-dive.md) |
| **Interview day strategy** | 45-min script, phrases, cheat sheet | [06-interview-playbook.md](06-interview-playbook.md) |
| **Reinforcement learning & bandits** | MDPs, Q-learning, PPO, exploration, RLHF | [16-reinforcement-learning.md](16-reinforcement-learning.md) |
| **Time series & forecasting** | ARIMA, backtesting, demand forecasting, anomalies | [17-time-series-and-forecasting.md](17-time-series-and-forecasting.md) |
| **Recommender systems** | collaborative filtering, two-tower, ranking, bias, cold start | [18-recommender-systems.md](18-recommender-systems.md) |
| **Speech & audio** | ASR, TTS, WER, voice agents | [19-speech-and-audio.md](19-speech-and-audio.md) |
| **Graph ML** | GNNs, knowledge graphs, GraphRAG, fraud rings | [20-graph-ml.md](20-graph-ml.md) |
| **Generative & multimodal AI** | diffusion, vision-language models, multimodal RAG | [21-generative-and-multimodal-ai.md](21-generative-and-multimodal-ai.md) |
| **AI agents** | tool use, planning, memory, agent evaluation & platforms | [22-ai-agents.md](22-ai-agents.md) |
| **Industry / domain rounds** | how AI is used and questioned in 20 industries | [23-industry-playbooks.md](23-industry-playbooks.md) |
| **General system design (any engineer)** | news feed, video streaming, ride-hailing, payments, Google Docs… | [24-classic-system-design-cases.md](24-classic-system-design-cases.md) |
| **Data engineering & SQL** | modeling, pipelines, Spark, 20+ SQL problems | [25-data-engineering-and-sql.md](25-data-engineering-and-sql.md) |
| **Cloud & infrastructure** | AWS/GCP/Azure, Kubernetes, GPUs, cost | [26-cloud-and-infrastructure-for-ml.md](26-cloud-and-infrastructure-for-ml.md) |
| **Security, privacy & responsible AI** | attacks on ML, privacy law, fairness, governance | [27-security-privacy-responsible-ai.md](27-security-privacy-responsible-ai.md) |
| **AI product sense** | framing problems, metrics, ROI, AI UX | [28-ai-product-sense.md](28-ai-product-sense.md) |
| **Senior / staff / lead rounds** | strategy, leadership, hiring, incidents | [29-senior-and-leadership.md](29-senior-and-leadership.md) |

---

## Step 2: Learn the one method for all "what if" questions

> **C**larify → **L**ayer map → **H**ypotheses (ranked) → **I**solate (how to prove it) → **F**ix (now + long-term) → **P**revent (monitoring/evals)

Read [03-debugging-framework.md](03-debugging-framework.md) **first**. It works for RAG, ML models, training bugs, data pipelines, and infrastructure.

---

## Step 3: Follow a plan

### 10-week full plan (from zero)
| Week | Theory (1-1.5 h/day) | Practice (1 h/day) |
|---|---|---|
| 1 | 07 ML fundamentals | 14 DSA patterns 1-2 |
| 2 | 11 Statistics + 07 what-ifs | 12 ML coding §1-5 |
| 3 | 08 Deep learning | 14 DSA patterns 3-5 |
| 4 | 09 NLP & LLMs | 12 ML coding §6-12 |
| 5 | 10 Computer vision (skip if not CV role) + 03 framework | 14 DSA patterns 6-9 |
| 6 | 01 System design fundamentals | 04 scenarios A-B (out loud) |
| 7 | 02 ML & LLM systems + 13 MLOps | 04 scenarios C-F |
| 8 | 05 Case studies 1-4 | 14 DSA patterns 10-12 |
| 9 | 05 Case studies 5-11 + 15 project prep | 2 full mock interviews |
| 10 | 06 playbook, revise weak areas | 4 mock interviews (mixed rounds) |

### Weeks 11-14: specialize (pick what fits your target job)
| Week | Track A: AI specialist | Track B: Software / data | Track C: Senior roles |
|---|---|---|---|
| 11 | 18 Recommenders or 19 Speech or 16 RL | 24 Classic cases 1-7 | 28 Product sense |
| 12 | 21 Generative & 22 Agents | 24 Classic cases 8-20 | 29 Leadership |
| 13 | 17 Time series or 20 Graph ML | 25 Data engineering & SQL | 27 Security & responsible AI |
| 14 | 23 Your industry + 27 | 26 Cloud & infra | 23 Your industry + mocks |

### 2-week emergency plan (interview soon)
| Days | Focus |
|---|---|
| 1-2 | 03 framework + 04 scenarios (your domain sections) |
| 3-4 | 07 + 08 Q&A (read questions, answer out loud) |
| 5-6 | 09 (or 10 for CV) + 11 |
| 7-8 | 02 + 05 case studies 1, 4, 5 |
| 9-10 | 12 ML coding (top 6) + DSA patterns 1, 3, 7 |
| 11-12 | 15: write 2 project deep dives + 6 STAR stories |
| 13-14 | Mocks + 06 cheat sheet |

### By role: what to prioritize
| Role | Highest priority files |
|---|---|
| **AI / LLM Engineer** | 03, 04, 02, 09, 05, 13, 15 |
| **ML Engineer** | 07, 08, 12, 13, 02, 04, 05, 14 |
| **Data Scientist / Applied Scientist** | 07, 11, 12, 08, 15, 05 (#4-5) |
| **NLP Engineer** | 09, 08, 12, 04 (A-B), 02 |
| **CV Engineer** | 10, 08, 12, 13, 05 (#7-8) |
| **MLOps Engineer** | 13, 26, 02, 01, 04 (C-E), 05 (#3) |
| **Recommender / Ranking Engineer** | 18, 07, 11, 05 (#4, #6), 23 (e-commerce, ads, media) |
| **Speech / Voice AI Engineer** | 19, 08, 09, 22, 12 |
| **RL / Robotics Engineer** | 16, 08, 10, 23 (autonomous vehicles) |
| **Forecasting / Quant / Supply-chain DS** | 17, 07, 11, 25, 23 (finance, logistics, energy) |
| **GenAI / Agents Engineer** | 22, 21, 09, 02, 04, 27, 28 |
| **Data Engineer** | 25, 26, 01, 24, 13 |
| **Backend / Software Engineer** | 01, 24, 05 (#9-11), 14, 26 |
| **Senior / Staff / Lead / Manager** | 29, 28, 06, 15, plus your role's files |

### Interviewing in a specific industry?
Read the general files for your role, then your industry in [23-industry-playbooks.md](23-industry-playbooks.md). Its last table tells you which other chapters matter most for that industry.

---

## Step 4: Practice the right way
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
| 16 | [Reinforcement learning & bandits](16-reinforcement-learning.md) |
| 17 | [Time series & forecasting](17-time-series-and-forecasting.md) |
| 18 | [Recommender systems](18-recommender-systems.md) |
| 19 | [Speech & audio](19-speech-and-audio.md) |
| 20 | [Graph ML](20-graph-ml.md) |
| 21 | [Generative & multimodal AI](21-generative-and-multimodal-ai.md) |
| 22 | [AI agents](22-ai-agents.md) |
| 23 | [Industry playbooks (20 industries)](23-industry-playbooks.md) |
| 24 | [Classic system design cases](24-classic-system-design-cases.md) |
| 25 | [Data engineering & SQL](25-data-engineering-and-sql.md) |
| 26 | [Cloud & infrastructure for ML](26-cloud-and-infrastructure-for-ml.md) |
| 27 | [Security, privacy & responsible AI](27-security-privacy-responsible-ai.md) |
| 28 | [AI product sense](28-ai-product-sense.md) |
| 29 | [Senior & leadership rounds](29-senior-and-leadership.md) |

---

## Rebuild the PDF
```bash
pip install markdown pygments
python scripts/build_pdf.py      # needs Chrome or Edge installed
```

## Contributing
Found a mistake, or want to add a scenario question you were asked in a real interview? Open an issue or a pull request.
New "what if" scenarios should follow the same format: **causes (ranked) → how to isolate → fix (now / long-term) → prevent.**

If this helped you, give the repo a star so others can find it.

## License
Content is licensed under [CC BY 4.0](LICENSE): free to share and adapt, with credit.
