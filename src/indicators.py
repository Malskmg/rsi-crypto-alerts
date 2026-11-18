import pandas as pd
from ta.momentum import RSIIndicator


def compute_rsi(df: pd.DataFrame, period: int = 14) -> float:
    rsi_series = RSIIndicator(close=df["close"], window=period).rsi()
    latest_rsi = rsi_series.iloc[-1]

    if pd.isna(latest_rsi):
        raise ValueError("RSI non disponible : pas assez de bougies.")

    return float(latest_rsi)