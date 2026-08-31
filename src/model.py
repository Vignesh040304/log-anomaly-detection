"""Isolation Forest anomaly model."""
from __future__ import annotations
import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyModel:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=250, contamination=contamination,
            random_state=random_state, n_jobs=-1
        )

    def fit(self, X):
        self.model.fit(X)
        return self

    def predict(self, X):
        return self.model.predict(X)

    def score(self, X):
        raw = -self.model.decision_function(X)
        lo, hi = float(np.min(raw)), float(np.max(raw))
        if np.isclose(lo, hi):
            return np.full_like(raw, 50.0, dtype=float)
        return 100 * (raw - lo) / (hi - lo)
