import pandas as pd
import numpy as np


# ============================================================
# 1) Daily → Weekly resample
# ============================================================
def resample_to_weekly(df_daily):
    df_weekly = df_daily.resample("W").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last"
    })
    df_weekly.dropna(inplace=True)
    return df_weekly


# ============================================================
# 2) Pivot Highs & Lows (CLOSE-based lows)
# ============================================================
def find_pivots(df):
    highs = df["High"].values
    closes = df["Close"].values
    dates = df.index

    pivot_highs = []
    pivot_lows = []

    for i in range(1, len(df) - 1):

        # Pivot High
        if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
            pivot_highs.append((dates[i], highs[i]))

        # Pivot Low USING CLOSE (institutional swing low)
        if closes[i] < closes[i-1] and closes[i] < closes[i+1]:
            pivot_lows.append((dates[i], closes[i]))

    return pivot_highs, pivot_lows


# ============================================================
# 3) Trend Reversal Confirmation (BOS + % Rise + Midpoint)
# ============================================================
def is_reversal_confirmed(df, idx_low):
    closes = df["Close"].values
    highs = df["High"].values

    swing_low = closes[idx_low]

    # Look ahead 10 weeks max
    end = min(idx_low + 10, len(df)-1)

    future_closes = closes[idx_low+1:end+1]
    future_highs = highs[idx_low+1:end+1]

    local_max_close = future_closes.max()
    local_max_high = future_highs.max()

    # A) % Rise ≥ 8%
    rise_pct = (local_max_close - swing_low) / swing_low * 100
    if rise_pct >= 8:
        return True

    # B) BOS — wick break of previous candle high
    if local_max_high > highs[idx_low - 1]:
        return True

    # C) Midpoint reclaim
    prev_high = df["High"].iloc[idx_low - 1]
    prev_low = df["Low"].iloc[idx_low - 1]
    midpoint = (prev_high + prev_low) / 2

    if local_max_close > midpoint:
        return True

    return False


# ============================================================
# 4) Final Supports (Correct Gap Logic + Weekly Zone Width)
# ============================================================
def detect_supports(df_daily):
    df = resample_to_weekly(df_daily)
    pivot_highs, pivot_lows = find_pivots(df)

    supports = []
    last_support_price = None  # store price only

    for date_low, swing_low in pivot_lows:

        idx_low = df.index.get_loc(date_low)

        # Must confirm reversal (trend break)
        if not is_reversal_confirmed(df, idx_low):
            continue

        # ---- Build current zone (±2.5% = 5% wide) ----
        curr_zone_low = swing_low * 0.975
        curr_zone_high = swing_low * 1.025

        # ---- Apply spacing rule correctly ----
        if last_support_price is not None:

            prev_zone_low = last_support_price * 0.975
            prev_zone_high = last_support_price * 1.025

            # CORRECT GAP LOGIC:
            # Gap = curr_low - prev_zone_high
            gap_pct = (curr_zone_low - prev_zone_high) / prev_zone_high * 100

            # Accept only if gap 14–17%
            if not (14 <= gap_pct <= 17):
                continue

        # ---- Add final support ----
        supports.append({
            "date": str(date_low.date()),
            "price": round(swing_low, 2),
            "zone_low": round(curr_zone_low, 2),
            "zone_high": round(curr_zone_high, 2)
        })

        # Update last support PRICE only
        last_support_price = swing_low

    return supports
