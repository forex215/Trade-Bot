from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from sklearn.ensemble import RandomForestClassifier


class SignalModel:
    def __init__(self) -> None:
        self.model = RandomForestClassifier(n_estimators=120, random_state=42)
        self.last_trained: datetime | None = None
        self.trained = False

    def train_if_needed(self, df: pd.DataFrame) -> None:
        now = datetime.now(timezone.utc)
        if self.trained and self.last_trained and now - self.last_trained < timedelta(minutes=15):
            return

        train_df = df.copy()
        train_df["target"] = (train_df["close"].shift(-1) > train_df["close"]).astype(int)
        train_df = train_df.dropna().reset_index(drop=True)

        features = train_df[["rsi_14", "macd", "macd_signal", "ema_200", "returns"]]
        y = train_df["target"]
        if len(features) < 50:
            self.trained = False
            return

        self.model.fit(features, y)
        self.trained = True
        self.last_trained = now

    def predict_buy_probability(self, row: pd.Series) -> float:
        if not self.trained:
            return 0.5
        X = pd.DataFrame(
            [
                {
                    "rsi_14": row["rsi_14"],
                    "macd": row["macd"],
                    "macd_signal": row["macd_signal"],
                    "ema_200": row["ema_200"],
                    "returns": row["returns"],
                }
            ]
        )
        proba = self.model.predict_proba(X)[0]
        return float(proba[1])
