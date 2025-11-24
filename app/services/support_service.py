import pandas as pd
import numpy as np


# 1) Daily → Weekly resample
def resample_to_weekly(df_daily):
    df_weekly = df_daily.resample("W").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last"
    })
    df_weekly.dropna(inplace=True)
    return df_weekly


# 2) Pivot highs/lows (using CLOSE for lows)
def find_pivots(df):
    highs = df["High"].values
    closes = df["Close"].values
    dates = df.index

    pivot_highs = []
    pivot_lows = []

    for i in range(1, len(df) - 1):

        # Pivot high
        if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
            pivot_highs.append((dates[i], highs[i]))

        # Pivot low USING CLOSE (not wick)
        if closes[i] < closes[i-1] and closes[i] < closes[i+1]:
            pivot_lows.append((dates[i], closes[i]))

    return pivot_highs, pivot_lows


# 3) Trend reversal confirmation (Hybrid BOS + % rise)
def is_reversal_confirmed(df, idx_low):
    closes = df["Close"].values
    highs = df["High"].values

    swing_low = closes[idx_low]

    # Look ahead 10 weeks max
    end = min(idx_low + 10, len(df)-1)

    local_max_close = closes[idx_low+1:end+1].max()
    local_max_high = highs[idx_low+1:end+1].max()

    # A) % Rise ≥ 8%
    if (local_max_close - swing_low) / swing_low * 100 >= 8:
        return True

    # B) Wick BOS — any high breaks previous candle high
    if local_max_high > highs[idx_low-1]:
        return True

    # C) Reclaim structure — close > midpoint of previous candle
    midpoint = (df["High"].iloc[idx_low-1] + df["Low"].iloc[idx_low-1]) / 2
    if local_max_close > midpoint:
        return True

    return False


# 4) Final supports with spacing rule + correct 5% zone
def detect_supports(df_daily):
    df = resample_to_weekly(df_daily)
    pivot_highs, pivot_lows = find_pivots(df)

    supports = []
    last_support = None

    for date_low, swing_low in pivot_lows:

        idx_low = df.index.get_loc(date_low)

        # Must confirm reversal
        if not is_reversal_confirmed(df, idx_low):
            continue

        # Spacing rule 14–17%
        if last_support is not None:
            gap_pct = (swing_low - last_support) / last_support * 100
            if not (14 <= gap_pct <= 17):
                continue

        # Support zone = ±2.5% (5% total width)
        zone_low = swing_low * 0.975
        zone_high = swing_low * 1.025

        supports.append({
            "date": str(date_low.date()),
            "price": round(swing_low, 2),
            "zone_low": round(zone_low, 2),
            "zone_high": round(zone_high, 2)
        })

        last_support = swing_low

    return supports
