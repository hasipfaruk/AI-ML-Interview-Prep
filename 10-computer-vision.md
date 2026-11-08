# 10. Computer Vision

### Contents
1. [Core tasks](#1-core-tasks)
2. [Key concepts & models](#2-key-concepts--models)
3. [Metrics](#3-metrics)
4. [Data & augmentation](#4-data--augmentation)
5. [Deployment](#5-deployment)
6. [What-if scenarios (CV)](#6-what-if-scenarios)

---

## 1. Core tasks
| Task | Output | Typical models |
|---|---|---|
| Classification | one label per image | ResNet, EfficientNet, ViT, ConvNeXt |
| Object detection | boxes + labels | YOLO family, Faster R-CNN, DETR, RT-DETR |
| Semantic segmentation | class per pixel | U-Net, DeepLab, SegFormer |
| Instance segmentation | mask per object | Mask R-CNN, SAM (promptable) |
| Keypoints / pose | body/face points | HRNet, OpenPose |
| OCR | text from image | detection + recognition (CRNN), TrOCR, document AI models |
| Image similarity / retrieval | embedding | CLIP, DINOv2, metric learning |
| Generation | images | Diffusion models |
| Vision-language | captions, VQA | CLIP, multimodal LLMs |
| Video | actions, tracking | 3D CNN, video transformers, SORT/DeepSORT/ByteTrack |

## 2. Key concepts & models

**Q: One-stage vs two-stage detectors?** Two-stage (Faster R-CNN): region proposals then classify → more accurate, slower. One-stage (YOLO, SSD, RetinaNet): predict boxes directly → fast, real-time.

**Q: Anchor boxes?** Predefined box shapes the model adjusts. Anchor-free detectors (FCOS, newer YOLOs, DETR) predict directly.

**Q: Non-Maximum Suppression (NMS)?** Remove duplicate boxes: keep highest-score box, drop others with IoU above threshold. Too low threshold → misses overlapping objects (crowds).

**Q: IoU?** Intersection area / union area of predicted vs ground-truth box.

**Q: U-Net?** Encoder-decoder with skip connections that keep fine spatial detail. Standard for segmentation (especially medical).

**Q: Vision Transformer (ViT)?** Split image into patches, embed them as tokens, apply Transformer. Needs lots of data or pretraining; less built-in inductive bias than CNNs.

**Q: CLIP?** Image encoder + text encoder trained contrastively on image-text pairs → shared embedding space → zero-shot classification and image search with text.

**Q: Transfer learning in CV?** Start from ImageNet/foundation-model weights; replace head; fine-tune. Big gains when you have little data.

**Q: Focal loss?** Down-weights easy examples, focuses on hard ones. Fixes foreground/background imbalance in detection.

**Q: Self-supervised learning in vision?** SimCLR/MoCo (contrastive), MAE (masked patches), DINO. They learn features without labels.

## 3. Metrics
- Classification: accuracy, precision/recall/F1, top-5 accuracy, confusion matrix.
- Detection: **mAP** (mean Average Precision across classes) at IoU 0.5 or averaged over 0.5:0.95 (COCO).
- Segmentation: mIoU, Dice coefficient.
- Generation: FID, CLIP score, human eval.
- Production: latency (ms/frame), FPS, model size.

## 4. Data & augmentation
- Augmentations: flips, crops, rotation, color jitter, blur, noise, cutout, mixup, cutmix, mosaic (YOLO). **Must be label-preserving** (don't flip text/digits; for detection, transform boxes too).
- Labeling: bounding boxes / polygons tools (CVAT, Label Studio), label QA, active learning.
- Synthetic data for rare cases.
- Normalize with the same mean/std used in pretraining.

## 5. Deployment
- Edge (mobile, cameras): quantization (INT8), pruning, distillation, TensorRT/ONNX/CoreML/TFLite, smaller backbones (MobileNet, EfficientNet-Lite).
- Video pipelines: decode → sample frames (not every frame) → batch inference → tracking to smooth → events.
- Trade-off: accuracy vs FPS vs power.

## 6. What-if scenarios

### Model works in the lab but fails on real camera images.
Domain shift: lighting, angle, blur, resolution, compression, camera sensor. Collect production samples, label, fine-tune; augmentation matching real conditions; check preprocessing (RGB vs BGR, resize method, normalization).

### Detector misses small objects.
Higher input resolution, feature pyramid (FPN), tiling/slicing large images (SAHI), anchor sizes tuned, more small-object training examples.

### Too many false positives at night.
Night data under-represented → collect/augment low-light data, separate threshold or model for night, IR-aware preprocessing, hard negative mining.

### Model is accurate but too slow for real-time on edge device.
Smaller backbone, quantization, pruning, distillation, lower resolution, TensorRT, skip frames + tracking between detections.

### Model learned the background instead of the object ("cows on grass" problem).
Spurious correlation. Use Grad-CAM to see where the model looks, diversify backgrounds, augmentation (cutout, background replacement), counterfactual examples.

### Medical images: only 200 labeled scans.
Transfer learning (from domain-specific pretrained models), heavy augmentation, self-supervised pretraining on unlabeled scans, cross-validation, expert-in-the-loop active learning, careful patient-level splits (no same patient in train & test!).

### Overlapping objects in crowds are missed.
NMS threshold too aggressive → tune, Soft-NMS, or NMS-free detectors (DETR).

### Accuracy dropped after a camera firmware update.
Input distribution changed (color profile, compression). Monitor input statistics (brightness, blur), detect drift, recalibrate/fine-tune.

### OCR fails on handwritten or rotated text.
Deskew/rotation correction, specific handwriting models, fine-tune on domain data, multimodal LLM fallback with confidence checks.
