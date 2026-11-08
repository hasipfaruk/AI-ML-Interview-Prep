# 09. NLP & LLMs (Theory + Scenarios)

### Contents
1. [Classic NLP](#1-classic-nlp)
2. [Tokenization](#2-tokenization)
3. [Embeddings](#3-embeddings)
4. [Transformers & pretrained models](#4-transformers--pretrained-models)
5. [How LLMs are trained](#5-how-llms-are-trained)
6. [Using LLMs: prompting, decoding, fine-tuning](#6-using-llms)
7. [LLM limitations & evaluation](#7-llm-limitations--evaluation)
8. [What-if scenarios (NLP/LLM)](#8-what-if-scenarios)

(For RAG and LLM system design, see [02](02-ml-and-llm-systems.md) and [04](04-what-if-scenarios.md).)

---

## 1. Classic NLP

**Q: Text preprocessing steps?** Lowercasing, tokenization, removing punctuation/stopwords, stemming (crude chop: "running"→"run") vs lemmatization (dictionary form: "better"→"good"), normalization. *Note:* for Transformers you mostly skip this and use the model's own tokenizer on raw text.

**Q: Bag of Words vs TF-IDF?** BoW counts words. TF-IDF = term frequency × inverse document frequency → down-weights common words. Both ignore word order and meaning.

**Q: BM25?** Improved TF-IDF ranking function (term frequency saturation + document length normalization). Still the strong baseline for keyword search.

**Q: n-grams?** Sequences of n words. They capture some local order ("not good").

**Q: Classic NLP tasks?** Text classification, sentiment, NER (named entity recognition), POS tagging, parsing, machine translation, summarization (extractive vs abstractive), question answering, topic modeling (LDA), coreference resolution.

**Q: What is NER and how to build it today?** Labeling spans like PERSON/ORG/DATE. Token classification with BIO tags using a fine-tuned BERT-style model; or LLM with structured output for low-data cases.

**Q: Language model perplexity?** exp(average negative log-likelihood per token). Lower = model less "surprised". Comparable only with the same tokenizer.

## 2. Tokenization

**Q: Word vs character vs subword tokenization?** Word: huge vocab, out-of-vocabulary problem. Character: long sequences. **Subword** (BPE, WordPiece, Unigram/SentencePiece): frequent words whole, rare words split into pieces → no OOV, compact.

**Q: How does BPE work?** Start with characters, repeatedly merge the most frequent adjacent pair into a new token until vocab size reached.

**Q: Why do tokenizers matter in interviews / production?**
- Cost and context limits are in tokens.
- Non-English languages often use more tokens per word → higher cost, worse performance.
- Numbers and code tokenized oddly → arithmetic/spelling weaknesses.
- **Mismatched tokenizer between training and serving = garbage outputs.**

## 3. Embeddings

**Q: Word2Vec?** Learns word vectors by predicting context words (Skip-gram) or the word from context (CBOW). Similar words → close vectors; analogies (king − man + woman ≈ queen). GloVe: from co-occurrence matrix. FastText: subword n-grams → handles rare words.

**Q: Static vs contextual embeddings?** Static: one vector per word ("bank" same everywhere). Contextual (BERT, etc.): vector depends on the sentence.

**Q: Sentence embeddings?** Models trained with **contrastive learning** (pull similar pairs together, push others apart). Examples: Sentence-BERT, E5, BGE, OpenAI/Cohere embeddings. Used for semantic search, clustering, RAG.

**Q: Bi-encoder vs cross-encoder?** Bi-encoder encodes query and document separately → precompute document vectors → fast retrieval. Cross-encoder reads query + document together → more accurate, slow → used for **reranking** top results.

**Q: Cosine similarity vs dot product?** Cosine ignores magnitude; equals dot product on normalized vectors. Use what the embedding model was trained with.

## 4. Transformers & pretrained models

(Attention mechanics in [08 §4](08-deep-learning.md#transformers).)

**Q: BERT vs GPT?**
| BERT | GPT |
|---|---|
| Encoder-only, bidirectional | Decoder-only, left-to-right (causal mask) |
| Pretrained with masked language modeling (MLM) (+NSP originally) | Pretrained with next-token prediction |
| Best for understanding: classification, NER, embeddings | Best for generation, general-purpose LLMs |

**Q: T5?** Encoder-decoder, every task as text-to-text.

**Q: Why did Transformers replace RNNs?** Parallel training, better long-range dependencies, scale well with data and compute.

**Q: What is the context window and what limits it?** Max tokens the model can attend to. Limited by O(n²) attention cost, KV-cache memory, and positional encoding trained lengths (extended via RoPE scaling).

**Q: KV cache?** During generation, store Keys and Values of previous tokens so each new token only computes attention for itself → much faster decoding, but memory grows with sequence length × batch.

**Q: Mixture of Experts (MoE)?** Many expert FFNs, a router activates only a few per token → huge parameter count with lower compute per token. Challenges: load balancing, memory.

## 5. How LLMs are trained

```
1. Pretraining:              next-token prediction on trillions of tokens (web, books, code). Learns language + knowledge.
2. SFT (instruction tuning): fine-tune on (instruction, good response) pairs. Learns to follow instructions/chat format.
3. Preference alignment:     RLHF (reward model + PPO) or DPO (direct preference optimization) on (chosen, rejected) pairs.
                             Learns helpful, harmless, honest behavior.
(+ reasoning training with RL on verifiable rewards, like math and code, for "thinking" models)
```
**Q: RLHF in simple words?** Humans compare two answers → train a reward model to predict preference → optimize the LLM with RL (PPO) to maximize reward, with a KL penalty to stay close to the original model (avoid reward hacking).

**Q: DPO vs RLHF?** DPO skips the reward model and RL loop; directly optimizes the model on preference pairs with a classification-like loss. Simpler, more stable.

**Q: Scaling laws?** Loss decreases predictably as a power law with model size, data, and compute. Chinchilla: for a compute budget, train smaller models on more data (~20 tokens per parameter) than earlier practice.

**Q: Emergent abilities / in-context learning?** Large models can learn a task from examples in the prompt without weight updates.

## 6. Using LLMs

**Q: Decoding strategies?**
| Method | Behavior |
|---|---|
| Greedy | Always pick top token. Deterministic, can be repetitive |
| Beam search | Keep top-k sequences. Good for translation, bland for chat |
| Temperature | <1 sharper (more deterministic), >1 more random |
| Top-k | sample from k most likely tokens |
| Top-p (nucleus) | sample from smallest set with cumulative prob ≥ p |
| Repetition/frequency penalty | discourage repeats |

**Q: Prompting techniques?** Clear instructions + role, few-shot examples, chain-of-thought / reasoning, output format specification (JSON schema), delimiters for untrusted input, self-consistency (sample several, vote), decomposition, ReAct (reason + tool use).

**Q: Fine-tuning methods?**
- **Full fine-tuning:** all weights; expensive, risk of forgetting.
- **PEFT:** LoRA (low-rank adapters on attention/MLP weights; trains <1% of params), **QLoRA** (LoRA on 4-bit quantized base → fine-tune big models on one GPU), prefix/prompt tuning, adapters.
- **Q: How does LoRA work?** Freeze W; learn ΔW = B·A with small rank r. At inference merge or swap adapters. Hyperparameters: rank r, alpha, target modules, LR.

**Q: When fine-tune vs RAG vs prompt?** See [02 §12](02-ml-and-llm-systems.md#12-decision-tables). One-liner: *"RAG for knowledge, fine-tuning for behavior/format/cost, prompting first always."*

**Q: Structured output?** JSON mode / function calling / constrained decoding (grammar) + schema validation + retry.

**Q: Small vs large models?** Small: cheaper, faster, can be fine-tuned and self-hosted, good for narrow tasks (classification, extraction). Large: better reasoning, generalization, fewer examples needed.

## 7. LLM limitations & evaluation

**Q: Why do LLMs hallucinate?** They're trained to produce plausible next tokens, not verified truths; knowledge gaps/cutoffs; training rewarded confident answers; no grounding. Mitigate: RAG with citations, "I don't know" option, lower temperature, verification step, tool use (calculator, search).

**Q: Other limitations?** Knowledge cutoff, context limits, lost-in-the-middle, sensitivity to prompt wording, weak arithmetic without tools, bias, prompt injection, cost/latency, non-determinism.

**Q: How to evaluate LLMs?**
- Benchmarks (MMLU, GSM8K, HumanEval…) for general capability. Watch out for contamination (test data leaked into training).
- **Task-specific eval set** built from real use. This matters most.
- Metrics: exact match / F1 (QA), BLEU/ROUGE (translation/summarization; they correlate weakly with quality), BERTScore, pass@k (code), LLM-as-judge with rubrics, human eval, pairwise preference (win rate).
- Safety/red-teaming, consistency, latency, cost.

## 8. What-if scenarios

### Your text classifier works on English but fails on Hinglish / code-mixed text.
Data mismatch. Collect & label code-mixed samples, use multilingual model (XLM-R, mBERT, multilingual LLM), transliteration normalization, augmentation via translation, evaluate per language.

### Sentiment model misclassifies sarcasm and negation ("not bad at all").
BoW/TF-IDF models ignore order → use contextual models (fine-tuned Transformer); add targeted training examples; error analysis with slices (negation, sarcasm).

### Fine-tuned LLM outputs repeat the same phrase endlessly.
Decoding: add repetition penalty, adjust temperature/top-p, set max tokens, stop sequences. Training: check EOS token included in training data (a common bug: the model never learned to stop), data has duplicates, chat template mismatch.

### Fine-tuned model ignores the instruction format after training.
**Chat template mismatch** between training and inference (system/user/assistant tags), loss computed on prompt tokens instead of only response tokens, too few epochs or LR too low.

### LLM answers well in testing, but users report it is "dumb" for some queries.
Collect failing examples, categorize (missing knowledge → RAG; reasoning → bigger model / CoT; format → prompt/fine-tune; ambiguity → clarifying questions). Build eval set from real failures.

### NER model misses new product names.
Out-of-distribution entities. Gazetteers/dictionaries, active learning on new data, regular retraining, LLM-based extraction with few-shot examples, character/subword features.

### Embedding search returns semantically similar but wrong results ("cancel subscription" matches "subscribe").
Embeddings capture topic not intent/negation. Use hybrid with keyword, fine-tune embeddings with hard negatives, add a cross-encoder reranker, intent classifier.

### Summarization model produces facts not in the source.
Abstractive hallucination. Faithfulness checks (NLI entailment, QA-based), constrain with extractive-first, lower temperature, fine-tune on faithful data, citations.

### Context window is too small for a 300-page document.
Chunk + map-reduce summarization, RAG, hierarchical summarization, long-context model (trade-off: cost, lost-in-the-middle).

### LLM gives different answer quality for the same prompt in different languages.
Tokenization inefficiency + less training data in that language. Translate-in/translate-out pipeline, multilingual eval, language-specific few-shot examples.

### Model output contains toxic or biased content.
Input/output safety classifiers, system prompt policies, preference tuning with safety data, red-teaming, human review loops, logging and incident process.

### Training an LLM: loss stops improving early.
Data quality/duplication, LR schedule, tokenizer issues, too-small model for data (capacity), check for data loading bugs (same shard repeated), monitor gradient norm.
