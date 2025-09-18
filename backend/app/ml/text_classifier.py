import os
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
MODEL_PATH = os.path.join(ARTIFACT_DIR, "text_clf.joblib")
VECTORIZER_PATH = os.path.join(ARTIFACT_DIR, "tfidf.joblib")
MODEL_VERSION = "tfidf-logreg-v1"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _load_builtin_dataset() -> Tuple[List[str], List[str]]:
    """
    Load a tiny built-in dataset for bootstrap training when no artifact exists.
    This is NOT for production; replace with real datasets (LIAR, FakeNewsNet, etc.).
    """
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fake_news_samples.csv")
    texts: List[str] = []
    labels: List[str] = []
    with open(data_path, "r", encoding="utf-8") as f:
        # header: text,label
        next(f)
        for line in f:
            parts = line.rstrip("\n").split(",", 1)
            if len(parts) != 2:
                parts = line.rstrip("\n").rsplit(",", 1)
                if len(parts) != 2:
                    continue
            text, label = parts[0].strip(), parts[1].strip()
            if text and label:
                texts.append(text)
                labels.append(label)
    return texts, labels


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    reasons: List[str]
    token_importances: List[Tuple[str, float]]
    latency_ms: int


class TextClassifier:
    def __init__(self) -> None:
        _ensure_dir(ARTIFACT_DIR)
        self.model: LogisticRegression | None = None
        self.vectorizer: TfidfVectorizer | None = None
        self._load_or_train()

    def _load_or_train(self) -> None:
        model_exists = os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH)
        if model_exists:
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.model = joblib.load(MODEL_PATH)
            return

        texts, labels = _load_builtin_dataset()
        vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=30000,
            min_df=1,
        )
        X = vectorizer.fit_transform(texts)
        y = np.array(labels)

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        clf = LogisticRegression(max_iter=1000, class_weight="balanced")
        clf.fit(X_train, y_train)

        try:
            report = classification_report(y_val, clf.predict(X_val))
            print("[TextClassifier] Bootstrap training report:\n" + report)
        except Exception:
            pass

        joblib.dump(vectorizer, VECTORIZER_PATH)
        joblib.dump(clf, MODEL_PATH)

        self.vectorizer = vectorizer
        self.model = clf

    def predict(self, text: str) -> ClassificationResult:
        if self.model is None or self.vectorizer is None:
            raise RuntimeError("Model not initialized")

        start = time.time()
        X = self.vectorizer.transform([text])
        probabilities = self.model.predict_proba(X)[0]
        classes = list(self.model.classes_)
        best_index = int(np.argmax(probabilities))
        best_label = str(classes[best_index])
        best_confidence = float(probabilities[best_index])

        token_scores = self._compute_token_contributions(text)
        reasons = [f"Top cues: {', '.join([tok for tok, _ in token_scores[:3]])}"] if token_scores else []

        latency_ms = int((time.time() - start) * 1000)
        return ClassificationResult(
            label=best_label,
            confidence=best_confidence,
            reasons=reasons,
            token_importances=token_scores[:20],
            latency_ms=latency_ms,
        )

    def _compute_token_contributions(self, text: str) -> List[Tuple[str, float]]:
        """
        Approximate token importance by mapping unigrams in the input to the
        corresponding logistic regression weights times TF-IDF value.
        """
        assert self.model is not None and self.vectorizer is not None

        analyzer = self.vectorizer.build_analyzer()
        tokens = analyzer(text)
        X = self.vectorizer.transform([text])
        vocab: Dict[str, int] = self.vectorizer.vocabulary_  # type: ignore[attr-defined]

        coefs = self.model.coef_
        if coefs.ndim == 2 and coefs.shape[0] > 1:
            weights = np.max(coefs, axis=0)
        else:
            weights = coefs[0]

        X_csr = X.tocsr()
        idx_to_value: Dict[int, float] = {int(i): float(v) for i, v in zip(X_csr.indices, X_csr.data)}

        token_to_score: Dict[str, float] = {}
        for token in tokens:
            if token in vocab:
                feat_idx = vocab[token]
                tfidf_val = idx_to_value.get(feat_idx, 0.0)
                score = tfidf_val * float(weights[feat_idx])
                token_to_score[token] = token_to_score.get(token, 0.0) + score

        sorted_tokens = sorted(token_to_score.items(), key=lambda kv: abs(kv[1]), reverse=True)
        return sorted_tokens


_GLOBAL_CLASSIFIER: TextClassifier | None = None


def get_text_classifier() -> TextClassifier:
    global _GLOBAL_CLASSIFIER
    if _GLOBAL_CLASSIFIER is None:
        _GLOBAL_CLASSIFIER = TextClassifier()
    return _GLOBAL_CLASSIFIER