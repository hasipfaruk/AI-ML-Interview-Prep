# 21. Generative & Multimodal AI

Image, video and audio generation, vision-language models, and multimodal RAG.
Text LLMs are in [09-nlp-and-llms.md](09-nlp-and-llms.md); basic generative model types (VAE, GAN) are in [08 §6](08-deep-learning.md#6-generative-models).

### Contents
1. [The generative model families](#1-the-generative-model-families)
2. [Diffusion models in depth](#2-diffusion-models-in-depth)
3. [Controlling and customizing image generation](#3-controlling-and-customizing-image-generation)
4. [Video, audio and 3D generation](#4-video-audio-and-3d-generation)
5. [Vision-language models (VLMs)](#5-vision-language-models-vlms)
6. [Multimodal RAG and document understanding](#6-multimodal-rag-and-document-understanding)
7. [Evaluation](#7-evaluation)
8. [Serving and cost](#8-serving-and-cost)
9. [Safety, copyright and trust](#9-safety-copyright-and-trust)
10. [System design: an image generation product](#10-system-design-an-image-generation-product)
11. [What-if scenarios](#11-what-if-scenarios)

---

## 1. The generative model families

| Family | Idea | Strengths | Weaknesses |
|---|---|---|---|
| **Autoregressive** | generate one token at a time | text, code, also images/audio as tokens | slow for long outputs |
| **VAE** | encode to latent distribution, decode samples | smooth latent space, fast | blurry outputs alone |
| **GAN** | generator vs discriminator | sharp, very fast sampling | unstable training, mode collapse |
| **Diffusion** | learn to remove noise step by step | best quality and diversity, stable training | slow sampling (many steps) |
| **Flow matching / rectified flow** | learn a straight path from noise to data | fewer steps, used in newer image/video models | newer, similar ideas to diffusion |

**Q: Why did diffusion replace GANs for most image generation?** More stable training, better diversity (no mode collapse), scales well with data and text conditioning. GANs are still used where speed matters (super-resolution, real-time filters).

## 2. Diffusion models in depth

**Q: Forward process?** Take a real image and add a little Gaussian noise over T steps (e.g., 1000) until it is pure noise. This is fixed, not learned.

**Q: Reverse process?** A neural network learns to remove noise one step at a time. Starting from pure noise and running the reverse process produces a new image.

**Q: What does the network actually predict?** Usually the **noise ε** that was added (ε-prediction). Alternatives: predict the clean image (x₀) or the "velocity" v. Training loss is simply MSE between predicted and true noise:
```
1. pick a real image x0, a random step t, random noise ε
2. make noisy image x_t = sqrt(ᾱ_t)·x0 + sqrt(1-ᾱ_t)·ε
3. loss = || ε - model(x_t, t, text) ||²
```

**Q: Noise schedule?** How much noise is added at each step (linear, cosine). It affects quality, especially at high resolution.

**Q: Which architecture?** Originally a **U-Net** with attention layers. Newer models use **Diffusion Transformers (DiT)**, which treat latent patches as tokens and scale better.

**Q: How is text used (conditioning)?** A text encoder (CLIP text encoder, T5) turns the prompt into embeddings; the denoiser attends to them through **cross-attention**.

**Q: Classifier-free guidance (CFG)?** Train the model sometimes with the prompt and sometimes without (empty prompt). At sampling, push the prediction away from the unconditional one:
`ε = ε_uncond + w · (ε_cond − ε_uncond)`.
Higher guidance scale w → follows prompt more closely but less diverse and can look over-saturated. Typical w ≈ 5-8.

**Q: Negative prompts?** Replace the empty prompt in CFG with things to avoid ("blurry, extra fingers").

**Q: Samplers (schedulers)?** DDPM (many steps, slow), DDIM (deterministic, fewer steps), DPM-Solver / Euler (good quality in 20-30 steps). Same model, different speed/quality trade-off.

**Q: Latent diffusion (Stable Diffusion idea)?** Run diffusion in the small latent space of a VAE instead of pixel space (e.g., 64×64×4 instead of 512×512×3) → ~50× cheaper. VAE decoder turns the final latent into the image.

**Q: How to make sampling faster?** Fewer steps with better samplers, **distillation** (consistency models, progressive/adversarial distillation → 1-4 steps), smaller models, caching, fp16/quantization, TensorRT compilation.

**Q: Why are hands and text inside images often wrong?** Small, detailed structures with many valid configurations and less training data; VAE compression loses fine details; text rendering needs exact characters. Newer models with better text encoders and higher-resolution latents improve it.

## 3. Controlling and customizing image generation

| Technique | What it does |
|---|---|
| **Img2img** | start from a noised version of an input image instead of pure noise → keeps layout |
| **Inpainting / outpainting** | regenerate a masked region / extend the canvas |
| **ControlNet** | extra network that conditions on structure: edges, depth map, pose skeleton, segmentation |
| **IP-Adapter / image prompts** | use a reference image as a style or subject prompt |
| **LoRA for diffusion** | small low-rank adapters trained on 10-100 images to learn a style or object; swap per user |
| **DreamBooth** | fine-tune to bind a rare token to a specific subject ("sks dog") |
| **Textual inversion** | learn a new word embedding for a concept, model frozen |
| **Super-resolution / upscalers** | generate small, then upscale |

**Q: Fine-tuning risks for diffusion?** Overfitting (every image looks like the training images), language drift (forgets what "dog" means in general). Fix with prior-preservation loss, fewer steps, lower LR, LoRA instead of full fine-tune.

**Q: Brand consistency for a company?** Brand LoRA trained on approved assets + reference image adapters + fixed prompt templates + brand-safety classifier + human approval for public use.

## 4. Video, audio and 3D generation

**Q: How do video models differ from image models?** They generate many frames that must be **temporally consistent**. Approaches: 3D (space-time) attention or DiT over space-time patches, generating a low-frame-rate clip then interpolating, latent video VAEs. Main problems: flicker, identity drift, physics errors, huge compute.

**Q: Text-to-speech (TTS) pipeline?** Text → normalization (numbers, abbreviations) → acoustic model (predicts mel-spectrogram or audio tokens) → vocoder (turns it into waveform). Modern systems use neural codec tokens + autoregressive or diffusion models; voice cloning from a few seconds of audio.

**Q: Speech-to-text (ASR)?** Encoder-decoder Transformer on log-mel spectrograms (Whisper-style) or CTC models. Metrics: Word Error Rate (WER). Issues: accents, noise, code-switching, domain words.

**Q: Music/audio generation?** Audio tokenized by a neural codec, then a Transformer or diffusion model generates tokens conditioned on text or melody.

**Q: 3D generation?** Score distillation from 2D diffusion, NeRF / Gaussian splatting reconstruction from images, direct 3D diffusion on meshes/point clouds.

## 5. Vision-language models (VLMs)

**Q: CLIP?** Image encoder + text encoder trained with **contrastive loss** on hundreds of millions of image-caption pairs. Matching pairs are pulled together. Gives zero-shot classification ("a photo of a {label}") and image-text search. Weak at counting, spatial relations, reading text.

**Q: How do LLaVA-style multimodal LLMs work?**
```
Image → vision encoder (e.g., CLIP/SigLIP ViT) → patch embeddings
      → projector (MLP) maps them into the LLM's token space
      → LLM reads [image tokens] + [text tokens] → generates answer
```
Training: (1) align the projector on image-caption pairs, (2) instruction tune on visual Q&A / conversations.

**Q: Other designs?** Cross-attention from LLM to image features (Flamingo-style), Q-Former to compress image features (BLIP-2), natively multimodal models trained on interleaved image-text from the start.

**Q: Why do VLMs struggle with documents, charts and small text?** Image is resized to a low resolution (e.g., 336×336) → small text becomes unreadable. Fixes: high-resolution tiling ("any resolution": split into crops + a global view), OCR-free document models trained on documents, or combine with OCR output.

**Q: Image token cost?** A high-res image can be hundreds to thousands of tokens → latency and cost. Downscale when detail isn't needed; crop to the relevant region.

**Q: Common VLM tasks in industry?** Document extraction (invoices, IDs), visual Q&A for support (photo of a broken product), product tagging, content moderation, accessibility (alt text), chart/table understanding, UI understanding for computer-use agents.

**Q: VLM hallucination?** Describing objects that aren't there. Mitigate: ask for grounded answers (bounding boxes, quotes of visible text), verify with detectors/OCR, lower temperature, eval sets with "trick" images.

## 6. Multimodal RAG and document understanding

**Q: Problem?** Enterprise documents contain tables, charts, scanned pages, diagrams. Text-only parsing loses them.

**Q: Approaches?**
| Approach | How | Trade-off |
|---|---|---|
| **Parse to text** | OCR + layout parser, tables → Markdown/HTML, charts → captions generated by a VLM | cheap retrieval, may lose detail |
| **Caption everything** | VLM writes a description per image/chart, index the description | good recall, captioning cost at ingest |
| **Multimodal embeddings** | embed page images directly (CLIP-like or document-page retrievers that embed screenshots) | keeps visual layout, bigger index |
| **Hybrid** | retrieve by text, then send the original page image to a VLM for the answer | best quality, highest cost |

Normal RAG pipeline and its failures: [02 §7](02-ml-and-llm-systems.md#7-llm-systems-rag-in-depth), [04 section A](04-what-if-scenarios.md#a-rag-systems).

**Q: Tables specifically?** Keep tables whole as a chunk with headers repeated, store as Markdown/HTML, add a natural-language summary for retrieval, or load into a database and use text-to-SQL for numeric questions.

## 7. Evaluation

| Metric | Measures | Caveat |
|---|---|---|
| **FID** (Fréchet Inception Distance) | how close the distribution of generated images is to real ones (lower = better) | needs many samples, uses ImageNet features, doesn't check the prompt |
| **IS** (Inception Score) | quality and diversity | outdated, unreliable |
| **CLIP score** | similarity between prompt and image | can be gamed, weak on counting/relations |
| **Prompt-alignment benchmarks** | VQA-based checks: "is there a red cube left of a blue ball?" | closer to what users care about |
| **Human preference** | side-by-side ratings, Elo/win rate | gold standard, expensive |
| **Aesthetic / preference models** | learned predictors of human preference | biased to training raters |
| **TTS**: MOS (mean opinion score), WER of re-transcribed audio, speaker similarity |  |  |
| **VLM**: accuracy on VQA/document benchmarks + task-specific eval set |  |  |

**Q: How would you evaluate an image generation feature for a product?** Build a prompt set from real user prompts (by category), generate with fixed seeds, measure prompt alignment (VQA-based), human side-by-side preference vs current model, safety violation rate, latency and cost per image, and online: download/regenerate rate.

## 8. Serving and cost

**Q: Why is image generation expensive?** Each image = N denoising steps × a large network; video multiplies by frames. A GPU might produce a few to tens of images per second depending on model, resolution and steps.

**Cost/latency levers:**
- Fewer steps (better samplers, distilled 1-4 step models).
- Lower default resolution + upscaler only when the user wants to download.
- Batch requests on the GPU; queue with priority tiers (paid users first).
- fp16/bf16, quantization, compiled engines.
- Cache results for popular prompts / templates.
- Smaller "draft" previews, full quality on demand.
- Async jobs for video (minutes) with progress updates and notifications.

**Q: Real-time vs async?** Images: near real-time (a few seconds) with a queue. Video/long audio: always async jobs (submit → job ID → poll/webhook).

## 9. Safety, copyright and trust

**Q: Main risks?** Deepfakes of real people, sexual or violent content, minors, hate symbols, copyrighted characters/styles, trademarked logos, misinformation, voice cloning fraud.

**Q: Defenses?**
- **Input**: prompt classifiers, block lists for real-person names in sensitive contexts, policy-trained LLM filter.
- **Output**: image safety classifiers (nudity, violence, minors), face matching against protected persons where legally appropriate, logo detection.
- **Training data**: filter unsafe and opt-out content, licensed datasets, record data provenance.
- **Provenance**: invisible **watermarks** and signed **content credentials** (C2PA-style metadata) so generated media can be identified. Note: metadata can be stripped; watermarks can be weakened by editing. Use both and never rely on just one.
- **Voice**: consent verification for voice cloning, audio watermarking.
- **Human review and appeals** for borderline cases; abuse monitoring per account.

**Q: Copyright questions in interviews?** Say: training data licensing and opt-outs, avoid generating near-copies (memorization checks: compare outputs to training set with perceptual hashes), block specific protected characters/brands, legal review. Don't claim legal certainty.

## 10. System design: an image generation product

> "Design a text-to-image feature for a design app with 5M users."

```
Client → API gateway (auth, quota per plan)
      → Prompt service: safety check (input), prompt rewrite/expansion (LLM), template/brand params
      → Job queue (priority by plan) → GPU workers (autoscaled, batched, distilled model + LoRA hot-swap)
      → Output safety classifiers → watermark + content credentials
      → Object storage + CDN → client (progress via websocket/SSE)
Metadata DB: jobs, prompts, seeds, model version (for reproducibility and abuse investigations)
Monitoring: queue time, GPU utilization, cost/image, safety block rate, regenerate rate
```
Deep dives: LoRA hot-swapping per brand (keep base model loaded, swap small adapters), GPU autoscaling on queue length, fairness of the queue, reproducibility (seed + model version + sampler), abuse detection.

---

## 11. What-if scenarios

### Generated images ignore part of the prompt ("a red cube on a blue ball" → colors swapped).
**Causes (ranked):** text encoder weak at attribute binding (CLIP text encoder); guidance scale too low; prompt too long (truncated at the text encoder's token limit, often 77 tokens); concept rare in training data.
**Isolate:** test shorter prompts; vary guidance; check token count; compare with a stronger text encoder model.
**Fix now:** LLM prompt rewriting into clear, short descriptions; tune guidance; regional prompting / layout control (ControlNet, boxes).
**Long-term:** model with a stronger text encoder (T5/LLM-based), fine-tune on compositional data.
**Prevent:** compositional prompt eval set with VQA-based scoring.

### Faces and hands look distorted.
Low resolution of the face region in latent space, too few steps, aggressive distillation, LoRA overfitting. **Fix:** face/hand detailer pass (detect → inpaint at higher resolution), more steps, better base model, negative prompts, pose ControlNet.

### The multimodal model misreads numbers in charts or tables.
**Causes:** image downscaled (small text unreadable); model weak at chart reasoning; dense table.
**Isolate:** crop the region and retry; compare with OCR text.
**Fix:** high-res tiling/crops, OCR + VLM together (give extracted text as extra context), extract tables to structured data and compute answers with code/SQL, ask the model to quote values before reasoning.
**Prevent:** document/chart eval set with numeric exact-match checks.

### Image generation is too slow (12 s per image) and too expensive.
Trace: queue time vs GPU time. Fix: distilled few-step model, fewer steps, lower default resolution + optional upscale, batching, fp16 + compiled engine, autoscale on queue length, cache popular templates, previews first. Trade-off: quality. Measure it with human preference on a fixed prompt set.

### Outputs are brand-unsafe or off-brand (wrong colors, competitor logos).
Brand LoRA + reference-image conditioning, color palette constraints, logo/brand classifiers on output, prompt templates locked for non-expert users, human approval before publishing. Track off-brand rate from reviewer rejections.

### A user generated a deepfake of a real politician.
**Mitigate:** remove content, review account, preserve logs for investigation. **Causes:** prompt filter missed name variants/descriptions; image-to-image with an uploaded photo bypassed text checks.
**Fix:** checks on uploaded images too (face matching for public figures in restricted contexts), better prompt classifiers, watermark + content credentials on all outputs, rate limits for new accounts.
**Prevent:** red-team regularly with evasion prompts; abuse monitoring.

### The model generates near-copies of a training image.
Memorization (often from duplicated training images). Deduplicate training data, check outputs against training set with perceptual hashing, lower guidance, block exact-match outputs.

### Video output flickers between frames.
Temporal inconsistency. Use models with temporal attention, fewer independently generated frames (generate keyframes + interpolate), consistent seeds/latents, post-processing stabilization.

### Fine-tuned brand LoRA makes every image look the same.
Overfitting: too many steps, too-high LR, too few/too-similar training images. Lower rank/steps, more varied images, lower LoRA strength at inference, prior-preservation images.

### VLM answers confidently about objects that aren't in the photo.
Object hallucination. Ask for evidence (boxes or quotes), verify with an object detector/OCR, add "say not visible if unsure" instruction, evaluate on images designed to trick (absent-object questions).
