from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score

FEATURES = ["rsi_14", "macd", "macd_signal", "ema_200", "returns", "atr_14", "volatility_20"]


class SignalModel:
    def __init__(self, model_type: str = "rf") -> None:
        self.model_type = model_type
        self.model = self._build_model(model_type)
        self.last_trained: datetime | None = None
        self.trained = False
        self.last_metrics: dict = {}

    def _build_model(self, model_type: str):
        if model_type == "logreg":
            return LogisticRegression(max_iter=1200)
        return RandomForestClassifier(n_estimators=200, random_state=42, min_samples_leaf=5)

    def _prep(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["target"] = (out["close"].shift(-1) > out["close"]).astype(int)
        return out.dropna().reset_index(drop=True)

    def train_if_needed(self, df: pd.DataFrame) -> None:
        now = datetime.now(timezone.utc)
        if self.trained and self.last_trained and now - self.last_trained < timedelta(minutes=15):
            return
        self.train(df)

    def train(self, df: pd.DataFrame) -> dict:
        train_df = self._prep(df)
        if len(train_df) < 200:
            self.trained = False
            self.last_metrics = {"error": "Need at least 200 rows for robust training"}
            return self.last_metrics

        split_idx = int(len(train_df) * 0.8)
        train_set = train_df.iloc[:split_idx]
        test_set = train_df.iloc[split_idx:]

        X_train = train_set[FEATURES]
        y_train = train_set["target"]
        X_test = test_set[FEATURES]
        y_test = test_set["target"]

        self.model.fit(X_train, y_train)
        proba = self.model.predict_proba(X_test)[:, 1]
        preds = (proba >= 0.5).astype(int)

        self.trained = True
        self.last_trained = datetime.now(timezone.utc)
        self.last_metrics = {
            "rows": len(train_df),
            "accuracy": float(accuracy_score(y_test, preds)),
            "precision": float(precision_score(y_test, preds, zero_division=0)),
            "buy_threshold": 0.5,
        }
        return self.last_metrics

    def predict_buy_probability(self, row: pd.Series) -> float:
        if not self.trained:
            return 0.5
        X = pd.DataFrame([{f: row[f] for f in FEATURES}])
        proba = self.model.predict_proba(X)[0]
        return float(proba[1])
