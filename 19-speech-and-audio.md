# 19 — Speech & Audio AI

Asked for voice assistants, call-center AI, meeting transcription, voice agents, media, accessibility and smart-device roles.

### Contents
1. [Audio basics](#1-audio-basics)
2. [Audio features](#2-audio-features)
3. [Speech recognition (ASR)](#3-speech-recognition-asr)
4. [ASR evaluation](#4-asr-evaluation)
5. [Text-to-speech (TTS)](#5-text-to-speech-tts)
6. [Speaker tasks: diarization, verification](#6-speaker-tasks-diarization-verification)
7. [Wake word, VAD & audio classification](#7-wake-word-vad--audio-classification)
8. [Data & augmentation](#8-data--augmentation)
9. [Voice agents: system design](#9-voice-agents-system-design)
10. [Deployment](#10-deployment)
11. [What-if scenarios (speech)](#11-what-if-scenarios)

---

## 1. Audio basics

**Q: What is a digital audio signal?** A sequence of amplitude samples taken at a fixed rate (the **sampling rate**). Each sample is stored with some **bit depth** (16-bit is common).

**Q: Common sampling rates?** 8 kHz (telephone), 16 kHz (most speech models), 22.05/24 kHz (TTS), 44.1/48 kHz (music, video). **Nyquist:** sampling rate must be at least 2× the highest frequency you want to capture. Telephone audio (8 kHz) loses everything above 4 kHz → harder ASR.

**Q: What breaks if sampling rates don't match?** A model trained on 16 kHz fed 8 kHz audio (or vice versa) without resampling produces garbage. Always resample to the model's expected rate.

**Q: Mono vs stereo?** Speech models usually take mono. In call centers, stereo with **agent and customer on separate channels** makes diarization trivial — keep it if available.

**Q: Audio formats/codecs?** WAV/PCM (uncompressed), FLAC (lossless), MP3/AAC/Opus (lossy). Telephony codecs (G.711 μ-law) and heavy compression reduce ASR accuracy.

## 2. Audio features

**Q: What is a spectrogram?** A time × frequency image showing energy at each frequency over time, computed with the **Short-Time Fourier Transform (STFT)** using small overlapping windows (e.g., 25 ms window, 10 ms hop).

**Q: Mel spectrogram?** Spectrogram with frequencies mapped to the **mel scale**, which matches human hearing (more resolution at low frequencies), usually with log amplitude. Standard input for modern speech models (e.g., 80 mel bins).

**Q: MFCC?** Mel-frequency cepstral coefficients — apply a DCT on the log mel spectrogram to get a compact (13–40) decorrelated representation. Classic for older ASR/speaker models; deep models now mostly use log-mel or raw waveform.

**Q: Raw waveform models?** wav2vec 2.0, HuBERT learn features directly from the waveform with self-supervised pretraining.

## 3. Speech recognition (ASR)

**Q: Classic ASR pipeline?** Acoustic model (audio → phonemes, HMM-GMM then HMM-DNN) + pronunciation lexicon + language model (n-gram) + decoder (WFST). Complex but controllable.

**Q: End-to-end ASR approaches?**
| Approach | Idea | Notes |
|---|---|---|
| **CTC** | predicts a label per frame including a "blank"; collapse repeats and blanks | no alignment needed; assumes frame outputs independent → benefits from external LM; streaming-friendly |
| **Attention encoder-decoder** (LAS, Whisper) | decoder attends to encoded audio and generates text | high accuracy; not naturally streaming; can **hallucinate** |
| **RNN-Transducer (RNN-T)** | encoder + prediction network + joiner | streaming, accurate — used in on-device assistants |
| Hybrid CTC/attention | multi-task | stable training |

**Q: Conformer?** Encoder combining convolution (local patterns) and self-attention (global context) — standard ASR encoder.

**Q: Self-supervised speech models?** wav2vec 2.0 / HuBERT / WavLM: pretrain on unlabeled audio by predicting masked parts, fine-tune with little labeled data → great for low-resource languages.

**Q: Whisper-style models?** Encoder-decoder Transformer trained on huge weakly-labeled multilingual data; does transcription, translation, language ID, timestamps. Strengths: robust to noise and accents. Weaknesses: 30-second windows, not truly streaming, can hallucinate text on silence/noise, slower than CTC models.

**Q: Streaming vs batch ASR?** Streaming outputs words while the user talks (needed for voice agents, live captions) — uses chunked/causal encoders, CTC or RNN-T, partial and final hypotheses. Batch processes full files — better accuracy (can see future context).

**Q: Role of a language model in ASR?** Rescoring or shallow fusion with an LM improves rare words and grammar. **Contextual biasing / hotwords** boost domain terms (product names, contact names).

**Q: Punctuation and casing?** Often a separate post-processing model (or built into models like Whisper). Also **inverse text normalization**: "twenty five dollars" → "$25".

## 4. ASR evaluation

**Q: WER?** Word Error Rate = (Substitutions + Deletions + Insertions) / number of words in reference. Can be > 100% (many insertions). **CER** (character error rate) for languages without spaces (Chinese, Japanese) or for names.

**Q: What normalization before WER?** Lowercase, remove punctuation, normalize numbers ("25" vs "twenty-five"), contractions — otherwise WER penalizes formatting, not recognition.

**Q: Beyond WER?** Entity/keyword error rate (did we get the account number right?), latency (first partial, final result), real-time factor (RTF = processing time / audio duration), WER by segment (accent, noise level, device), downstream task success (intent accuracy).

## 5. Text-to-speech (TTS)

**Q: TTS pipeline?** Text normalization ("Dr." → "doctor", numbers, dates) → grapheme-to-phoneme (pronunciation) → acoustic model (text/phonemes → mel spectrogram) → **vocoder** (mel → waveform).

**Q: Key TTS models?** Tacotron 2 (attention seq2seq → mel), FastSpeech 2 (non-autoregressive, fast, duration predictor), **VITS** (end-to-end with VAE + flow + GAN, no separate vocoder), neural codec language models (generate audio tokens, zero-shot voice cloning from a few seconds), diffusion/flow-matching TTS.

**Q: Vocoders?** WaveNet (high quality, slow), WaveRNN, **HiFi-GAN** (fast, high quality — common), neural audio codecs (EnCodec/SoundStream) for token-based models.

**Q: TTS evaluation?** **MOS** (mean opinion score from human raters), intelligibility (run ASR on output → WER), speaker similarity (embedding cosine), latency (time to first audio), naturalness of prosody.

**Q: Risks?** Voice cloning misuse (deepfakes, fraud) → consent, watermarking, speaker verification protections.

## 6. Speaker tasks: diarization, verification

**Q: Speaker diarization?** "Who spoke when." Pipeline: VAD → segment → speaker embeddings (x-vectors, ECAPA-TDNN) → clustering (spectral, agglomerative) → handle overlaps. End-to-end neural diarization (EEND) handles overlapping speech. Metric: **DER** (diarization error rate: missed speech + false alarm + speaker confusion).

**Q: Speaker verification vs identification?** Verification: "is this the claimed person?" (1:1, voice login). Identification: "which of N people is this?" (1:N). Metric: **EER** (equal error rate). Threat: replay attacks and synthetic voices → anti-spoofing / liveness detection.

## 7. Wake word, VAD & audio classification

**Q: Wake word detection ("Hey device")?** Tiny always-on model on device (low power), small CNN/RNN on mel features; then cloud verification to reduce false accepts. Metrics: false accept rate per hour vs false reject rate.

**Q: VAD (voice activity detection)?** Detects speech vs non-speech. Critical for: cutting silence before ASR (cost, hallucination prevention), end-of-turn detection in voice agents, diarization.

**Q: Audio classification / event detection?** Classify sounds (glass breaking, cough, music genre, machine faults). Use log-mel + CNN (PANNs) or audio transformers (AST), or pretrained audio embeddings (CLAP, BEATs). Multi-label is common.

## 8. Data & augmentation

**Q: Data augmentation for speech?** **SpecAugment** (mask random time and frequency bands on spectrogram — the most important trick), speed perturbation (0.9×/1.1×), adding background noise (MUSAN), room impulse responses (reverb), codec/telephony simulation, volume changes, pitch shift.

**Q: Where does labeled data come from?** Public datasets (LibriSpeech, Common Voice), in-house transcriptions, pseudo-labeling with a strong model + filtering by confidence, synthetic speech from TTS for rare words.

**Q: Privacy concerns?** Voice is biometric personal data. Consent, PII redaction in transcripts (card numbers, names), retention limits, on-device processing when possible.

## 9. Voice agents: system design
> "Design a phone voice agent that books appointments."

**Pipeline (cascaded):**
```
Caller audio (telephony / WebRTC, 8–16 kHz)
  → streaming VAD + end-of-turn detection
  → streaming ASR (partial + final transcripts, with hotwords for names/services)
  → LLM (dialogue + tools: check_availability, book_slot) — stream tokens
  → streaming TTS (start speaking after first sentence/phrase)
  → audio back to caller
Barge-in: if the caller starts talking while TTS plays → stop TTS immediately, listen
Logging, transcripts with PII redaction, human handoff, analytics
```
**Latency budget (target ~0.8–1.2 s from user stops talking → agent starts speaking):**
| Stage | Typical |
|---|---|
| End-of-turn detection | 200–500 ms (biggest hidden delay) |
| ASR final | 100–300 ms |
| LLM time to first token | 200–500 ms |
| TTS time to first audio | 100–300 ms |
| Network/telephony | 100–200 ms |

**Ways to cut latency:** streaming everywhere, smarter end-of-turn models (semantic + acoustic, not just silence timeout), start LLM on partial transcripts (speculatively), small/fast LLM for routine turns, short first sentence, filler phrases ("Let me check that…") while tools run, colocate services, cache common responses.

**Alternative:** **speech-to-speech models** (audio in, audio out, one model) — lower latency, better prosody and emotion, but less control, harder to debug, tool use and guardrails are harder. Cascaded is easier to inspect and improve per stage.

**Deep dives to mention:** dialogue state and slot confirmation ("Tuesday 3 PM, correct?"), spelling of names/emails (letter-by-letter mode, confirmation), DTMF keypad fallback, handling silence and noisy lines, human escalation, compliance (call recording disclosure), evaluation with simulated callers, metrics (task completion, average handle time, transfer rate, latency p95).

## 10. Deployment
- On-device: small models (quantized Conformer/RNN-T), wake word, privacy, offline use.
- Server: GPU batching for batch transcription, streaming servers with WebSockets/gRPC, autoscaling by concurrent streams.
- Cost drivers: audio hours processed; reduce with VAD (skip silence), smaller models for easy audio, batch processing for non-real-time.

---

## 11. What-if scenarios

Use the C.L.H.I.F.P. method from [03-debugging-framework.md](03-debugging-framework.md). Speech layer map: **microphone/telephony → codec/sampling → VAD → ASR (acoustic + LM) → post-processing (punctuation, ITN) → downstream NLU/LLM → TTS → playback**.

### High WER for users with certain accents
**Causes:** training data under-represents those accents; LM lacks local vocabulary/names; code-switching (mixing languages).
**Isolate:** WER sliced by accent/region/language; look at error types (substitutions on names vs common words).
**Fix (now):** contextual biasing/hotwords for local names, choose a more robust multilingual model.
**Fix (long-term):** collect and transcribe accent-specific data, fine-tune (or adapters), pseudo-label large unlabeled local audio, code-switching training data.
**Prevent:** per-segment WER dashboard; fairness checks before release.

### Accuracy is terrible on noisy call-center audio
**Causes:** 8 kHz narrowband telephony while model trained on 16 kHz clean audio; background noise; heavy compression; crosstalk.
**Isolate:** compare WER on clean vs call audio; check sampling rate pipeline (accidental resampling bugs, wrong μ-law decoding).
**Fix:** use telephony-trained or fine-tuned models, augment training with noise + codec simulation, noise suppression (careful — can hurt ASR), use stereo channel separation, hotwords for domain terms.

### The voice bot is too slow — users talk over it or hang up
Trace each stage (see §9 budget). Usual culprits: end-of-turn silence timeout too long, non-streaming ASR or TTS, big LLM, sequential tool calls, cross-region hops. Fix with streaming, better turn detection, smaller model routing, fillers during tool calls, colocation. Monitor p95 "user stopped → bot started" latency.

### ASR outputs text that was never said (hallucinations on silence or music)
**Cause:** encoder-decoder models (Whisper-style) generate plausible text when there's no speech (e.g., "Thank you for watching!"), repeat loops on long audio.
**Fix:** VAD to remove non-speech before ASR, confidence/no-speech probability thresholds, compression-ratio and repetition checks, chunking with overlap, CTC/RNN-T models for critical uses, temperature fallback settings.
**Prevent:** test sets with silence, music, hold music and noise.

### Diarization mixes up speakers
**Causes:** similar voices, short turns, overlapping speech, wrong number of speakers estimated, mono audio with crosstalk.
**Fix:** use separate channels when available, set known speaker count, overlap-aware models (EEND), longer minimum segment length, enroll known speakers (agent voice prints), post-correction with LLM using conversation context.

### TTS mispronounces names, brands, or numbers
**Fix:** custom pronunciation lexicon / phoneme input (SSML `<phoneme>`), text normalization rules (read "2024" as year vs number), test sets of domain words, for multilingual names use language tags. Prevent: pronunciation regression tests.

### Transcripts contain customers' card numbers and personal data
Security/compliance issue. Pause storage, redact PII (regex + NER on transcripts, audio bleeping), pause recording during payment (DTMF), restrict access, retention policy, audit.

### Wake word triggers on TV ads or random speech
High false accept rate. Collect false-trigger samples (hard negatives) and retrain, two-stage verification (on-device + cloud), adjust thresholds, speaker-aware wake word, detect audio from TV (echo/far-field cues).

### ASR misses domain terms (drug names, product codes)
Contextual biasing, custom LM/vocabulary, fine-tuning with domain audio, post-correction with fuzzy matching against a known entity list, LLM-based correction with constrained vocabulary.

### Live captions lag and keep changing words
Partial hypotheses are unstable. Show stable prefixes only, tune chunk size (latency vs stability trade-off), use streaming-native models (RNN-T), finalize faster on pauses.

### Voice cloning used to impersonate customers for account access
Add anti-spoofing (synthetic speech detection), multi-factor authentication instead of voice-only, liveness challenges (random phrases), monitor unusual patterns.
