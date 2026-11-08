# 08. Deep Learning (Theory + Training Debugging)

### Contents
1. [Neural network basics](#1-neural-network-basics)
2. [Optimization](#2-optimization)
3. [Regularization & normalization](#3-regularization--normalization)
4. [Architectures: CNN, RNN, Transformer](#4-architectures)
5. [Training at scale](#5-training-at-scale)
6. [Generative models](#6-generative-models)
7. [What-if: training debugging scenarios](#7-what-if-training-debugging-scenarios) (very commonly asked)

---

## 1. Neural network basics

**Q: What is a neuron / perceptron?** Weighted sum of inputs + bias, passed through a non-linear activation.

**Q: Why do we need non-linear activations?** Without them, stacked linear layers collapse into a single linear function, so the network couldn't learn non-linear patterns.

**Q: Common activations?**
| Activation | Notes |
|---|---|
| Sigmoid | 0 to 1, saturates → vanishing gradients; used for binary outputs |
| Tanh | −1 to 1, zero-centered, still saturates |
| ReLU | max(0,x); fast, no saturation for x>0; can "die" (always 0) |
| Leaky ReLU / PReLU | small slope for x<0 → fixes dying ReLU |
| GELU / SiLU (Swish) | smooth; used in Transformers/LLMs |
| Softmax | turns logits into a probability distribution (multi-class output) |

**Q: Explain backpropagation.** Forward pass computes outputs and loss. Backward pass applies the chain rule layer by layer from output to input to compute the gradient of the loss w.r.t. every weight. The optimizer then updates the weights.

**Q: Vanishing / exploding gradients?** Gradients multiplied through many layers shrink to ~0 (early layers stop learning) or blow up (NaN). Fixes: ReLU-family activations, good initialization (He/Xavier), normalization (BatchNorm/LayerNorm), residual connections, gradient clipping, LSTM/GRU gates for RNNs.

**Q: Why not initialize all weights to zero?** All neurons would compute the same thing and get the same gradients (symmetry), so they never differentiate. Use Xavier/Glorot (tanh/sigmoid) or He/Kaiming (ReLU).

**Q: Loss functions?** MSE/MAE (regression), binary cross-entropy (binary), categorical cross-entropy (multi-class), focal loss (imbalance, detection), contrastive / triplet / InfoNCE (embeddings), KL divergence (distillation, VAEs).

**Q: Why cross-entropy with softmax?** Gradient becomes simply (predicted − true), stable and strong; corresponds to maximum likelihood.

## 2. Optimization

**Q: SGD vs Momentum vs Adam?**
- SGD: noisy updates, may generalize well, needs tuned LR.
- Momentum: accumulates velocity → faster, smoother through ravines.
- RMSProp: per-parameter LR scaled by recent gradient magnitude.
- **Adam**: momentum + RMSProp + bias correction; default choice. **AdamW**: decoupled weight decay, the standard for Transformers.

**Q: Learning rate is the most important hyperparameter. How do you pick it?** LR range test (increase LR, watch loss), then use **warmup + decay** schedule (cosine, step, linear decay). Too high → diverge/NaN; too low → slow/stuck.

**Q: Why warmup?** Early in training Adam's statistics are unreliable and weights random; large updates can destabilize (especially Transformers). Warmup ramps LR up gradually.

**Q: Batch size effects?** Larger batch: faster per epoch on GPUs, smoother gradients, may generalize slightly worse, needs larger LR (linear scaling rule). Limited by memory → gradient accumulation simulates large batches.

**Q: Local minima in deep learning?** In high dimensions most critical points are saddle points; SGD noise and momentum help escape. Many minima are similarly good.

## 3. Regularization & normalization

**Q: Dropout?** Randomly zero activations during training (rate p) → prevents co-adaptation, acts like ensemble. Off at inference (activations scaled accordingly).

**Q: BatchNorm vs LayerNorm?** BatchNorm normalizes each feature across the batch. It works well for CNNs, depends on batch size, and behaves differently in train vs eval (running stats). LayerNorm normalizes across the features of each sample. It doesn't depend on the batch and is used in Transformers/RNNs. RMSNorm: simpler LayerNorm used in modern LLMs.

**Q: Other regularizers?** Weight decay, data augmentation, early stopping, label smoothing, mixup/cutmix, stochastic depth.

**Q: Why use residual (skip) connections?** `output = F(x) + x` gives gradients a direct path backward → enables very deep networks (ResNet, Transformers) and makes it easy to learn identity.

## 4. Architectures

### CNNs
**Q: Why convolutions for images?** Local connectivity + weight sharing → far fewer parameters, translation equivariance, hierarchical features (edges → textures → objects).
**Q: Output size formula?** `(W − K + 2P) / S + 1`.
**Q: Pooling?** Downsamples, adds small translation invariance. Max vs average. Global average pooling before classifier.
**Q: 1×1 convolution?** Changes channel count cheaply, mixes channels (used in Inception/ResNet bottlenecks).
**Q: Receptive field?** Region of the input that affects one output unit; grows with depth, dilation, stride.
**Q: Famous models?** LeNet → AlexNet → VGG (deep 3×3) → GoogLeNet/Inception → ResNet (skip connections) → EfficientNet (compound scaling) → ViT (Transformers on patches) → ConvNeXt.

### RNNs
**Q: RNN problem?** Sequential (no parallelism), vanishing gradients over long sequences.
**Q: LSTM vs GRU?** LSTM: cell state + input/forget/output gates → long-term memory. GRU: fewer gates (update/reset), faster, often similar performance.

### Transformers
**Q: Explain self-attention.** Each token creates a Query, Key, Value. Attention weights = softmax(Q·Kᵀ / √d), which says how much each token should look at every other token. Output = weighted sum of Values. Captures long-range dependencies in parallel.
**Q: Why divide by √d?** Dot products grow with dimension → softmax saturates → tiny gradients. Scaling keeps variance stable.
**Q: Multi-head attention?** Several attention heads in parallel, each learns different relationships (syntax, coreference…), concatenated.
**Q: Positional encoding?** Attention is order-agnostic, so we add position info: sinusoidal, learned, or **RoPE** (rotary, used in modern LLMs), ALiBi.
**Q: Encoder vs decoder vs encoder-decoder?** Encoder-only (BERT): bidirectional, understanding tasks. Decoder-only (GPT, Llama): causal mask, generation. Encoder-decoder (T5, original Transformer): translation/summarization.
**Q: Complexity of attention?** O(n²) in sequence length (time + memory). Solutions: FlashAttention (IO-aware exact), sparse/sliding-window attention, linear attention, KV caching for inference.
**Q: Transformer block?** Multi-head attention → add & norm → feed-forward (MLP) → add & norm. Modern: pre-norm, RMSNorm, SwiGLU, RoPE, GQA.

## 5. Training at scale
- **Mixed precision** (fp16/bf16): faster, less memory; bf16 avoids overflow (no loss scaling needed); fp16 needs loss scaling.
- **Gradient accumulation:** simulate large batch.
- **Gradient checkpointing:** recompute activations in backward → less memory, ~30% slower.
- **Data parallel (DDP), FSDP/ZeRO, tensor parallel, pipeline parallel**: see [02 §3](02-ml-and-llm-systems.md#3-training-infrastructure).
- **Transfer learning / fine-tuning:** freeze early layers, train head, then unfreeze with low LR. **PEFT/LoRA**: train small low-rank adapters instead of full weights.
- **Knowledge distillation:** small student learns from teacher's soft probabilities (with temperature).
- **Quantization / pruning** for inference.

## 6. Generative models
**Q: Autoencoder vs VAE?** Autoencoder compresses and reconstructs. VAE learns a probabilistic latent space (mean + variance) with KL regularization → can sample new data; uses reparameterization trick.
**Q: GAN?** Generator vs discriminator in a min-max game. Problems: mode collapse, unstable training.
**Q: Diffusion models?** Learn to reverse a gradual noising process. Start from noise and denoise step by step. Stable, high quality (Stable Diffusion = diffusion in latent space + text conditioning via cross-attention, classifier-free guidance). Slower sampling (fixes: fewer steps, distillation).
**Q: Autoregressive models?** Generate one token at a time conditioned on previous (GPT).

---

## 7. What-if: training debugging scenarios

**General debugging recipe (say this first):**
> "Start small: overfit a single batch. If the model can't drive loss to ~0 on 1 batch, there's a bug, not a modelling problem. Then check data → model → loss → optimizer → evaluation, one at a time."

### Loss is NaN / Inf
**Causes:** LR too high; exploding gradients; log(0) or division by zero in custom loss; fp16 overflow; bad input data (NaN in features, corrupted images); sqrt/exp of large values.
**Fix:** lower LR, gradient clipping, add epsilon to log/division, use bf16 or loss scaling, check data for NaN (`torch.isnan(x).any()`), use `torch.autograd.detect_anomaly()`, use numerically stable built-ins (`CrossEntropyLoss` on logits, not softmax + log).

### Loss doesn't decrease at all
**Causes:** LR too low/high; forgot `optimizer.zero_grad()` or `optimizer.step()`; frozen layers by mistake; labels misaligned with inputs (shuffled separately); wrong loss for task (softmax applied twice); dead ReLUs; data not normalized; bug in data pipeline (all same image).
**Fix:** overfit one batch, visualize inputs + labels, check gradients are non-zero per layer, LR range test.

### Loss decreases, then suddenly spikes
**Causes:** LR too high after warmup, bad batch (outlier/corrupt data), exploding gradients, numerical instability in fp16.
**Fix:** gradient clipping, lower peak LR, longer warmup, skip/inspect the bad batch, bf16, restart from checkpoint.

### Training loss goes down, validation loss goes up
**Overfitting.** Early stopping, more data/augmentation, dropout, weight decay, smaller model, mixup. Also check val pipeline matches train preprocessing.

### Validation is better than training
Usually fine: dropout/augmentation are active only during training, train loss averaged over the epoch while val measured at the end. Also check val set isn't too easy/small or leaked.

### Model predicts the same class for every input
Class imbalance (use weights/focal loss), LR too high causing collapse, dead network, labels broken, final activation wrong.

### GPU out of memory (OOM)
Reduce batch size + gradient accumulation; mixed precision; gradient checkpointing; shorter sequences; smaller model / LoRA; free unused tensors (`del`, `torch.no_grad()` in eval; if you forget it, activations are kept in memory); avoid accumulating loss tensors with graph (`loss.item()`); FSDP/ZeRO offload.

### Training is very slow / GPU utilization low (30%)
Data loading bottleneck → more `num_workers`, `pin_memory`, prefetching, preprocess offline, faster storage formats; too-small batch; CPU-GPU sync calls (`.item()` every step); use mixed precision, `torch.compile`, larger batch.

### Results differ every run
Set seeds (python, numpy, torch, CUDA), deterministic algorithms (`torch.use_deterministic_algorithms`), fixed data order; some GPU ops are inherently non-deterministic. Report mean ± std over multiple seeds.

### Model works in notebook but bad after deployment
`model.eval()` not called (dropout/BatchNorm in training mode!); different preprocessing (normalization constants, resize, tokenizer version); different input format (RGB vs BGR, channel order); quantization changed accuracy.

### Fine-tuning a pretrained model makes it worse
LR too high (destroys pretrained weights → use 10-100× smaller LR), catastrophic forgetting, too few examples (freeze more layers, use LoRA), mismatched preprocessing vs pretraining.

### Accuracy plateaus at a certain level
Check label noise ceiling (human agreement), error analysis on mistakes, more/better data often beats architecture changes, LR schedule (decay), bigger model if underfitting.

### BatchNorm issues with batch size 1-2
Statistics unreliable → use GroupNorm/LayerNorm, freeze BN stats, or larger batch via accumulation (doesn't fix BN) / sync BN across GPUs.
