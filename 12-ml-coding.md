# 12. ML Coding Round (Implement From Scratch)

Interviewers ask you to code ML pieces using only NumPy (or PyTorch) in 30-45 minutes.
**Practice:** type each one from memory until you can do it in < 15 minutes. Talk while coding: shapes, edge cases, complexity.

### Contents
1. [Linear regression (gradient descent)](#1-linear-regression)
2. [Logistic regression](#2-logistic-regression)
3. [K-means](#3-k-means)
4. [k-Nearest Neighbors](#4-k-nearest-neighbors)
5. [Metrics: precision, recall, F1, AUC](#5-metrics)
6. [Softmax & cross-entropy (stable)](#6-softmax--cross-entropy)
7. [Scaled dot-product & multi-head attention](#7-attention)
8. [A 2-layer neural network with backprop](#8-two-layer-neural-network)
9. [Decision tree split (Gini)](#9-decision-tree-split)
10. [PyTorch training loop](#10-pytorch-training-loop)
11. [Cosine similarity top-k search](#11-cosine-similarity-top-k)
12. [BPE tokenizer merge step](#12-bpe-merge-step)
13. [Interview tips for coding rounds](#13-tips)

---

## 1. Linear regression
```python
import numpy as np

class LinearRegression:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr, self.epochs = lr, epochs

    def fit(self, X, y):                      # X: (n, d), y: (n,)
        n, d = X.shape
        self.w, self.b = np.zeros(d), 0.0
        for _ in range(self.epochs):
            y_hat = X @ self.w + self.b
            err = y_hat - y                   # (n,)
            dw = (2 / n) * X.T @ err          # gradient of MSE
            db = (2 / n) * err.sum()
            self.w -= self.lr * dw
            self.b -= self.lr * db
        return self

    def predict(self, X):
        return X @ self.w + self.b

# Closed form (normal equation): w = (XᵀX)⁻¹ Xᵀy  → O(d³), use np.linalg.lstsq for stability
```

## 2. Logistic regression
```python
def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))   # clip avoids overflow

class LogisticRegression:
    def __init__(self, lr=0.1, epochs=1000, l2=0.0):
        self.lr, self.epochs, self.l2 = lr, epochs, l2

    def fit(self, X, y):
        n, d = X.shape
        self.w, self.b = np.zeros(d), 0.0
        for _ in range(self.epochs):
            p = sigmoid(X @ self.w + self.b)
            dw = X.T @ (p - y) / n + self.l2 * self.w   # gradient of log loss (+ L2)
            db = (p - y).mean()
            self.w -= self.lr * dw
            self.b -= self.lr * db
        return self

    def predict_proba(self, X):
        return sigmoid(X @ self.w + self.b)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

def log_loss(y, p, eps=1e-12):
    p = np.clip(p, eps, 1 - eps)
    return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
```

## 3. K-means
```python
def kmeans(X, k, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    centroids = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        # distances: (n, k)
        dists = np.linalg.norm(X[:, None, :] - centroids[None, :, :], axis=2)
        labels = dists.argmin(axis=1)
        new = np.array([X[labels == j].mean(axis=0) if np.any(labels == j) else centroids[j]
                        for j in range(k)])               # keep old centroid if cluster empty
        if np.allclose(new, centroids):
            break
        centroids = new
    return centroids, labels
# Mention: k-means++ init, scaling features, O(n·k·d) per iteration.
```

## 4. k-Nearest Neighbors
```python
from collections import Counter

def knn_predict(X_train, y_train, X_test, k=3):
    preds = []
    for x in X_test:
        d = np.linalg.norm(X_train - x, axis=1)
        idx = np.argpartition(d, k)[:k]          # O(n) instead of full sort
        preds.append(Counter(y_train[idx]).most_common(1)[0][0])
    return np.array(preds)
```

## 5. Metrics
```python
def precision_recall_f1(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1

def roc_auc(y_true, scores):
    # AUC = probability a random positive scores higher than a random negative
    order = np.argsort(scores)
    ranks = np.empty(len(scores)); ranks[order] = np.arange(1, len(scores) + 1)
    n_pos = y_true.sum(); n_neg = len(y_true) - n_pos
    return (ranks[y_true == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    # (ties need average ranks; mention this in the interview)
```

## 6. Softmax & cross-entropy
```python
def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)    # numerical stability: subtract max
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)

def cross_entropy(logits, labels):             # logits (n, C), labels (n,) ints
    z = logits - logits.max(axis=1, keepdims=True)
    log_probs = z - np.log(np.exp(z).sum(axis=1, keepdims=True))   # log-softmax
    return -log_probs[np.arange(len(labels)), labels].mean()
# Gradient w.r.t. logits = softmax(logits) - one_hot(labels), divided by n
```

## 7. Attention
```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    # Q: (..., Lq, d), K: (..., Lk, d), V: (..., Lk, dv)
    d = Q.shape[-1]
    scores = Q @ K.swapaxes(-1, -2) / np.sqrt(d)       # (..., Lq, Lk)
    if mask is not None:
        scores = np.where(mask, scores, -1e9)          # mask=False → blocked
    weights = softmax(scores, axis=-1)
    return weights @ V, weights

def causal_mask(L):
    return np.tril(np.ones((L, L), dtype=bool))        # token i sees tokens ≤ i
```
```python
import torch, torch.nn as nn, torch.nn.functional as F

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.h, self.dk = n_heads, d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model)
        self.out = nn.Linear(d_model, d_model)

    def forward(self, x, causal=False):                # x: (B, L, D)
        B, L, D = x.shape
        q, k, v = self.qkv(x).chunk(3, dim=-1)
        # (B, L, D) -> (B, h, L, dk)
        q, k, v = [t.view(B, L, self.h, self.dk).transpose(1, 2) for t in (q, k, v)]
        scores = q @ k.transpose(-2, -1) / self.dk ** 0.5          # (B, h, L, L)
        if causal:
            mask = torch.triu(torch.ones(L, L, dtype=torch.bool, device=x.device), 1)
            scores = scores.masked_fill(mask, float('-inf'))
        attn = F.softmax(scores, dim=-1)
        y = (attn @ v).transpose(1, 2).contiguous().view(B, L, D)
        return self.out(y)
```

## 8. Two-layer neural network
```python
class TwoLayerNet:
    def __init__(self, d_in, d_hidden, n_classes, lr=0.1, seed=0):
        rng = np.random.default_rng(seed)
        self.W1 = rng.normal(0, np.sqrt(2 / d_in), (d_in, d_hidden))   # He init
        self.b1 = np.zeros(d_hidden)
        self.W2 = rng.normal(0, np.sqrt(2 / d_hidden), (d_hidden, n_classes))
        self.b2 = np.zeros(n_classes)
        self.lr = lr

    def step(self, X, y):                               # one gradient step, returns loss
        n = len(X)
        # forward
        h_pre = X @ self.W1 + self.b1
        h = np.maximum(0, h_pre)                        # ReLU
        logits = h @ self.W2 + self.b2
        probs = softmax(logits)
        loss = -np.log(probs[np.arange(n), y] + 1e-12).mean()
        # backward
        dlogits = probs.copy(); dlogits[np.arange(n), y] -= 1; dlogits /= n
        dW2 = h.T @ dlogits;      db2 = dlogits.sum(0)
        dh = dlogits @ self.W2.T
        dh_pre = dh * (h_pre > 0)                       # ReLU gradient
        dW1 = X.T @ dh_pre;       db1 = dh_pre.sum(0)
        # update
        for p, g in ((self.W1, dW1), (self.b1, db1), (self.W2, dW2), (self.b2, db2)):
            p -= self.lr * g
        return loss
```

## 9. Decision tree split
```python
def gini(y):
    _, counts = np.unique(y, return_counts=True)
    p = counts / counts.sum()
    return 1 - np.sum(p ** 2)

def best_split(X, y):
    best = (None, None, np.inf)                         # (feature, threshold, weighted gini)
    n = len(y)
    for f in range(X.shape[1]):
        for t in np.unique(X[:, f]):
            left = X[:, f] <= t
            if left.all() or (~left).all():
                continue
            g = (left.sum() * gini(y[left]) + (~left).sum() * gini(y[~left])) / n
            if g < best[2]:
                best = (f, t, g)
    return best
```

## 10. PyTorch training loop
```python
def train(model, train_loader, val_loader, epochs=10, lr=3e-4, device='cuda'):
    model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    loss_fn = nn.CrossEntropyLoss()
    best_val = float('inf')
    for epoch in range(epochs):
        model.train()
        for X, y in train_loader:
            X, y = X.to(device), y.to(device)
            opt.zero_grad()
            loss = loss_fn(model(X), y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        sched.step()

        model.eval()                                    # dropout/BN off
        val_loss, n = 0.0, 0
        with torch.no_grad():                           # no graph → saves memory
            for X, y in val_loader:
                X, y = X.to(device), y.to(device)
                val_loss += loss_fn(model(X), y).item() * len(y); n += len(y)
        val_loss /= n
        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), 'best.pt')   # checkpoint best model
        print(f'epoch {epoch}: val_loss={val_loss:.4f}')
```

## 11. Cosine similarity top-k
```python
def top_k_cosine(query, matrix, k=5):          # query (d,), matrix (n, d)
    q = query / np.linalg.norm(query)
    M = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    sims = M @ q
    idx = np.argpartition(-sims, k)[:k]
    idx = idx[np.argsort(-sims[idx])]          # sort the top-k only
    return idx, sims[idx]
# Brute force O(n·d). At scale, use an ANN index (HNSW/IVF). See 02 §7.
```

## 12. BPE merge step
```python
from collections import Counter

def bpe_train(words, num_merges):
    # words: list of strings; represent each as tuple of symbols
    vocab = Counter(tuple(w) + ('</w>',) for w in words)
    merges = []
    for _ in range(num_merges):
        pairs = Counter()
        for word, freq in vocab.items():
            for a, b in zip(word, word[1:]):
                pairs[(a, b)] += freq
        if not pairs:
            break
        best = max(pairs, key=pairs.get)
        merges.append(best)
        new_vocab = Counter()
        for word, freq in vocab.items():
            out, i = [], 0
            while i < len(word):
                if i < len(word) - 1 and (word[i], word[i + 1]) == best:
                    out.append(word[i] + word[i + 1]); i += 2
                else:
                    out.append(word[i]); i += 1
            new_vocab[tuple(out)] += freq
        vocab = new_vocab
    return merges
```

## 13. Tips
- Start by stating input/output shapes and assumptions. Write a tiny test example.
- Vectorize with NumPy; mention complexity (time & memory).
- Numerical stability: subtract max in softmax, clip in log/sigmoid, add epsilon.
- Edge cases: empty clusters, division by zero, ties, k > n.
- Other common asks: implement **dropout, batch norm forward, conv2d (naive loops), IoU + NMS, train/test split, stratified sampling, gradient check, beam search, top-p sampling, reservoir sampling, an LRU cache**.

### Bonus: IoU + NMS (CV interviews)
```python
def iou(a, b):                                  # boxes [x1, y1, x2, y2]
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
    return inter / (area(a) + area(b) - inter + 1e-9)

def nms(boxes, scores, thresh=0.5):
    order = np.argsort(scores)[::-1]
    keep = []
    while len(order):
        i = order[0]; keep.append(i)
        order = np.array([j for j in order[1:] if iou(boxes[i], boxes[j]) < thresh])
    return keep
```

### Bonus: Top-p (nucleus) sampling
```python
def top_p_sample(logits, p=0.9, temperature=1.0, rng=np.random.default_rng()):
    probs = softmax(logits / temperature)
    order = np.argsort(probs)[::-1]
    cum = np.cumsum(probs[order])
    cutoff = np.searchsorted(cum, p) + 1         # smallest set with mass ≥ p
    keep = order[:cutoff]
    kept = probs[keep] / probs[keep].sum()
    return rng.choice(keep, p=kept)
```
