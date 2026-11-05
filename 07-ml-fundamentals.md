# 07 — Machine Learning Fundamentals (Theory Round)

Format: **Q → short answer you can say in 30–60 seconds.** Then "what if" scenarios at the end.
Practice: cover the answer, say it out loud, compare.

### Contents
1. [Core concepts](#1-core-concepts)
2. [Bias, variance, regularization](#2-bias-variance-regularization)
3. [Linear & logistic regression](#3-linear--logistic-regression)
4. [Trees & ensembles](#4-trees--ensembles)
5. [Other classic algorithms](#5-other-classic-algorithms)
6. [Unsupervised learning](#6-unsupervised-learning)
7. [Evaluation & metrics](#7-evaluation--metrics)
8. [Data preparation & feature engineering](#8-data-preparation--feature-engineering)
9. [What-if scenarios (ML)](#9-what-if-scenarios)

---

## 1. Core concepts

**Q: Supervised vs unsupervised vs self-supervised vs reinforcement learning?**
Supervised: learn from labeled (x, y). Unsupervised: find structure without labels (clustering, dimensionality reduction). Self-supervised: create labels from the data itself (predict next token, masked word) — how LLMs are pretrained. RL: an agent learns by trial and error from rewards.

**Q: Classification vs regression?** Predict a category vs a continuous number.

**Q: Parametric vs non-parametric?** Parametric has a fixed number of parameters (linear regression). Non-parametric grows with data (kNN, decision trees can).

**Q: Generative vs discriminative?** Discriminative models P(y|x) (logistic regression). Generative models P(x, y) or P(x) (Naive Bayes, GPT, diffusion).

**Q: What is a loss function vs cost vs objective?** Loss: error for one example. Cost: average over dataset. Objective: what we optimize (cost + regularization).

**Q: What is gradient descent?** Iteratively move parameters opposite to the gradient of the loss: `w = w − lr · ∇L`. Batch (all data), stochastic (one sample), mini-batch (common).

**Q: Why train / validation / test split?** Train to fit, validation to tune hyperparameters/early stop, test to estimate final performance once. Using test for tuning = leakage → optimistic results.

**Q: What is cross-validation?** Split data into k folds; train on k−1, validate on 1, rotate; average. Gives a more reliable estimate with small data. Use **stratified** k-fold for imbalance, **time-series split** for temporal data, **group k-fold** when same user appears multiple times.

**Q: Curse of dimensionality?** In high dimensions data becomes sparse and distances become similar, so distance-based methods (kNN) degrade and you need far more data.

**Q: No Free Lunch theorem?** No single algorithm is best for all problems — choose by data and constraints.

## 2. Bias, variance, regularization

**Q: Bias-variance trade-off?** Bias = error from too-simple assumptions (underfitting). Variance = error from sensitivity to training data (overfitting). Total error = bias² + variance + noise. More complexity → lower bias, higher variance.

**Q: How do you detect overfitting / underfitting?**
| | Train error | Validation error |
|---|---|---|
| Underfitting | high | high |
| Overfitting | low | high (big gap) |
| Good fit | low | low, small gap |

**Q: How to fix overfitting?** More data, data augmentation, simpler model, regularization (L1/L2, dropout), early stopping, feature selection, ensembling/bagging, cross-validation for tuning.

**Q: How to fix underfitting?** More complex model, more/better features, less regularization, train longer.

**Q: L1 vs L2 regularization?** L1 (Lasso) adds |w| → pushes weights to exactly zero → feature selection. L2 (Ridge) adds w² → shrinks weights smoothly, handles correlated features. Elastic Net = both.

**Q: Why does L1 create sparsity?** Its penalty has a constant gradient (corner at zero in the constraint diamond), so the optimum often lands on an axis where weights are exactly zero.

## 3. Linear & logistic regression

**Q: Assumptions of linear regression?** Linearity, independent errors, homoscedasticity (constant error variance), normally distributed errors (for inference), no strong multicollinearity.

**Q: What is multicollinearity and why does it matter?** Features highly correlated → unstable, uninterpretable coefficients. Detect with VIF; fix with removal, PCA, or Ridge.

**Q: Logistic regression — how does it work?** Linear score → sigmoid → probability. Trained by minimizing **log loss (binary cross-entropy)**, which is maximum likelihood. Decision boundary is linear.

**Q: Why not MSE for logistic regression?** With sigmoid, MSE is non-convex and gives weak gradients; log loss is convex and penalizes confident wrong predictions strongly.

**Q: R² meaning?** Fraction of target variance explained by the model. Can be negative on test data if the model is worse than predicting the mean.

## 4. Trees & ensembles

**Q: How does a decision tree split?** Choose the feature/threshold that maximizes impurity reduction — Gini or entropy (information gain) for classification, variance/MSE for regression.

**Q: Bagging vs boosting?**
- **Bagging** (Random Forest): train many models in parallel on bootstrap samples, average them → **reduces variance**.
- **Boosting** (AdaBoost, Gradient Boosting, XGBoost, LightGBM, CatBoost): train models sequentially, each fixes previous errors → **reduces bias**. More prone to overfitting; needs tuning (learning rate, depth, n_estimators, early stopping).

**Q: Why does Random Forest use random feature subsets?** To decorrelate trees, so averaging reduces variance more.

**Q: Why is XGBoost/LightGBM so popular for tabular data?** Strong accuracy, handles missing values, regularization, fast (histogram-based splits), little preprocessing (no scaling needed). Usually beats deep learning on tabular data.

**Q: Feature importance in trees — caveats?** Impurity-based importance is biased toward high-cardinality features. Use permutation importance or SHAP.

**Q: Stacking?** Train a meta-model on predictions of several base models (use out-of-fold predictions to avoid leakage).

## 5. Other classic algorithms

**Q: kNN?** Predict using the k closest training points. Needs feature scaling; slow at prediction; suffers in high dimensions. Small k → overfit, large k → underfit.

**Q: Naive Bayes?** Bayes' rule assuming features are conditionally independent given the class. Fast, good baseline for text (spam). Use Laplace smoothing for unseen words.

**Q: SVM?** Find the hyperplane with maximum margin. Soft margin (C) allows errors. **Kernel trick** computes similarity in a higher-dimensional space without explicitly mapping (RBF, polynomial).

**Q: When would you choose a simple model over a complex one?** Small data, need interpretability (finance/health regulations), low latency, strong baseline, easier maintenance.

## 6. Unsupervised learning

**Q: K-means?** Pick k centroids, assign points to nearest, recompute centroids, repeat. Assumes spherical, similar-sized clusters; sensitive to init (use k-means++) and scaling. Choose k by elbow method / silhouette score.

**Q: K-means vs DBSCAN vs hierarchical?** DBSCAN finds arbitrary shapes and noise points, no k needed, but sensitive to eps. Hierarchical builds a dendrogram, good for small data.

**Q: PCA?** Projects data onto directions of maximum variance (eigenvectors of covariance matrix). Used for compression, visualization, removing correlation. Requires scaling. Linear only.

**Q: t-SNE / UMAP?** Non-linear dimensionality reduction for visualization. Distances between clusters in t-SNE are not meaningful.

**Q: Anomaly detection methods?** Statistical (z-score), Isolation Forest, One-class SVM, autoencoders (high reconstruction error = anomaly), density-based.

## 7. Evaluation & metrics

**Q: Confusion matrix terms?** TP, FP, TN, FN.
- **Precision** = TP / (TP+FP) — "of what I flagged, how much was right?" (care when false alarms are costly: spam filter).
- **Recall** = TP / (TP+FN) — "of all positives, how many did I catch?" (care when misses are costly: cancer, fraud).
- **F1** = harmonic mean of precision and recall.
- **Accuracy** misleading on imbalanced data.

**Q: ROC-AUC vs PR-AUC?** ROC plots TPR vs FPR across thresholds; AUC = probability a random positive ranks above a random negative. On heavy imbalance, ROC looks overly good — **PR-AUC** is more informative.

**Q: How to choose a threshold?** Based on business cost: minimize cost = FP·cost_FP + FN·cost_FN, or fix one constraint ("recall ≥ 95%") and maximize the other.

**Q: Calibration?** Predicted probability 0.8 should be right 80% of the time. Check with reliability diagram; fix with Platt scaling or isotonic regression. Matters when probabilities are used for decisions/pricing.

**Q: Regression metrics?** MAE (robust to outliers, interpretable), RMSE (penalizes big errors), MAPE (percent, breaks near zero), R².

**Q: Ranking metrics?** Precision@k, Recall@k, MRR, MAP, nDCG (accounts for position and graded relevance).

**Q: Offline metric vs online metric?** Offline (AUC on test set) is a proxy. Online (CTR, revenue, retention via A/B test) is what matters. They can disagree.

## 8. Data preparation & feature engineering

**Q: How do you handle missing values?** First ask *why* missing (random or meaningful?). Options: drop, impute (mean/median/mode, model-based, KNN), add "is_missing" indicator, use models that handle NaN (XGBoost).

**Q: How to handle categorical features?** One-hot (low cardinality), ordinal (ordered), target encoding (high cardinality — use out-of-fold to avoid leakage), hashing, learned embeddings.

**Q: When do you need feature scaling?** Distance/gradient-based models: kNN, SVM, k-means, PCA, linear/logistic regression with regularization, neural nets. Not needed for trees. Fit the scaler on **train only**.

**Q: How to handle imbalanced data?** Use proper metrics (PR-AUC, recall@precision); class weights; resampling (undersample majority, oversample minority, SMOTE — only on training data); threshold tuning; anomaly detection framing; collect more minority data.

**Q: What is data leakage? Examples?** Information in training that wouldn't be available at prediction time. Examples: scaling on full dataset before split; target encoding without folds; future data in time series; duplicate rows across train/test; a feature created after the outcome (e.g., "account_closed" predicting churn).

**Q: Outliers?** Investigate first (error or real?). Cap/winsorize, transform (log), robust models/losses (Huber, MAE), or remove if errors.

**Q: Feature selection methods?** Filter (correlation, mutual info), wrapper (recursive feature elimination), embedded (L1, tree importance), plus domain knowledge.

## 9. What-if scenarios

### Your model has 98% training accuracy but 70% validation accuracy. What do you do?
Overfitting. Check leakage/split first (duplicates? distribution difference between train and val?). Then: regularization, simpler model, more data/augmentation, early stopping, cross-validation, feature selection. Plot learning curves: if val improves with more data → collect data.

### Both training and validation accuracy are low.
Underfitting or bad data. Check labels quality, features informativeness, bugs (labels shuffled? wrong target column?). Try a more complex model, better features, less regularization. Compare to a simple baseline (predict majority class) — if you can't beat it, the problem is data, not model.

### Validation score is suspiciously high (99%).
Suspect **leakage** first: target-derived features, duplicates across splits, future info, ID columns correlated with target. Check top feature importances — a single dominating feature is a red flag.

### Model performs well on validation but poorly on test.
Overfit to validation through heavy tuning, or val/test come from different distributions. Use cross-validation, a fresh holdout, check distributions.

### You have only 500 labeled examples.
Simple models + strong regularization, cross-validation, transfer learning / pretrained embeddings, data augmentation, active learning (label the most uncertain), weak supervision, semi-supervised learning, LLM-assisted labeling with human verification.

### You have 1% positive class (fraud).
See §8 imbalance. Mention: never report accuracy; tune threshold on business cost; stratified splits.

### Features are highly correlated.
Fine for prediction with trees; problematic for interpreting linear coefficients. Use regularization (Ridge), PCA, or drop redundant ones.

### Model is accurate but stakeholders don't trust it.
Explainability: SHAP/LIME, feature importance, partial dependence; show examples; compare to simple interpretable baseline; calibrate probabilities; involve domain experts in error analysis.

### Model works for most users but fails for one segment.
Slice-based error analysis; check data representation; add segment features or separate model; fairness considerations.

### Training takes too long.
Sample data for iteration, fewer features, use LightGBM (fast), early stopping, distributed training, better hardware, cache preprocessing.

### Labels are noisy.
Estimate noise (relabel a sample), consensus labeling, robust losses, remove examples model confidently disagrees with (confident learning), more regularization.

### Data distribution changed after deployment.
Drift → see [04 #24](04-what-if-scenarios.md#24-model-performance-slowly-degrades-over-months).
