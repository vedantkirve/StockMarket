# app/services/rsi_service.py

import pandas as pd

def compute_rsi_support(df: pd.DataFrame, period: int = 14):
    close = df["Close"]

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    current_rsi = round(float(rsi.iloc[-1]), 2)

    # RSI support logic: near 40 region
    is_rsi_support = current_rsi >= 38 and current_rsi <= 42

    return {
        "current_rsi": current_rsi,
        "is_rsi_support": is_rsi_support,
        "support_zone": "38–42"
    }
