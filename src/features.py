"""Feature engineering for anomaly detection."""
from __future__ import annotations
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

class FeatureBuilder:
    numeric_columns = ["status_code", "response_ms", "message_length", "has_error_keyword"]

    def __init__(self, max_features: int = 3000):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), min_df=1, max_features=max_features, sublinear_tf=True
        )
        self.scaler = StandardScaler()

    def fit_transform(self, frame: pd.DataFrame):
        text = self.vectorizer.fit_transform(frame["normalized_message"].fillna(""))
        numeric = frame[self.numeric_columns].fillna(0).astype(float).to_numpy()
        numeric = self.scaler.fit_transform(numeric)
        return sparse.hstack([text, sparse.csr_matrix(numeric)], format="csr")

    def transform(self, frame: pd.DataFrame):
        text = self.vectorizer.transform(frame["normalized_message"].fillna(""))
        numeric = frame[self.numeric_columns].fillna(0).astype(float).to_numpy()
        numeric = self.scaler.transform(numeric)
        return sparse.hstack([text, sparse.csr_matrix(numeric)], format="csr")
