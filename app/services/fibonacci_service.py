# app/services/fibonacci_service.py

import pandas as pd

def compute_fibonacci_levels(df: pd.DataFrame):
    # Take recent 200 candles for accuracy
    data = df.tail(200)

    swing_high = data["High"].max()
    swing_low = data["Low"].min()

    diff = swing_high - swing_low

    fib_levels = {
        "0.236": swing_high - diff * 0.236,
        "0.382": swing_high - diff * 0.382,
        "0.500": swing_high - diff * 0.5,
        "0.618": swing_high - diff * 0.618,
        "0.786": swing_high - diff * 0.786
    }

    current_price = data["Close"].iloc[-1]

    hit_level = None

    for level, price in fib_levels.items():
        if abs(current_price - price) / price * 100 <= 2:  # within 2%
            hit_level = {
                "level": level,
                "level_price": round(price, 2),
                "current_price": round(float(current_price), 2)
            }
            break

    return {
        "swing_high": round(float(swing_high), 2),
        "swing_low": round(float(swing_low), 2),
        "fib_hit": hit_level
    }
