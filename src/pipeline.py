"""End-to-end log anomaly detection pipeline."""
from __future__ import annotations
import pandas as pd
from .features import FeatureBuilder
from .model import AnomalyModel
from .parser import parse_logs

class LogAnomalyPipeline:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        self.features = FeatureBuilder()
        self.model = AnomalyModel(contamination, random_state)

    def fit_text(self, text: str) -> pd.DataFrame:
        frame = parse_logs(text)
        if len(frame) < 10:
            raise ValueError("Please provide at least 10 log lines.")
        X = self.features.fit_transform(frame)
        self.model.fit(X)
        frame["prediction"] = self.model.predict(X)
        frame["anomaly_score"] = self.model.score(X).round(2)
        frame["is_anomaly"] = frame["prediction"].eq(-1)
        frame["severity"] = pd.cut(
            frame["anomaly_score"], bins=[-0.1, 60, 80, 100.1],
            labels=["Low", "Medium", "High"]
        ).astype(str)
        return frame.sort_values("anomaly_score", ascending=False).reset_index(drop=True)
