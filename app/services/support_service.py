import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN


# =====================================================
# 1) Weekly Resample
# =====================================================
def resample_to_weekly(df):
    df_weekly = df.resample("W").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum"
    }).dropna()
    return df_weekly


# =====================================================
# 2) Improved Pivot Detection (Rounded pivots)
# =====================================================
def detect_improved_pivots(df, window=4):
    lows = df['Low'].values
    highs = df['High'].values
    closes = df['Close'].values
    dates = df.index

    pivot_lows = []
    pivot_highs = []

    for i in range(window, len(df) - window):
        local_slice_low = lows[i - window:i + window + 1]
        local_slice_high = highs[i - window:i + window + 1]

        # Rounded bottom pivot
        if lows[i] == local_slice_low.min():
            pivot_lows.append((dates[i], lows[i]))

        # Rounded top pivot
        if highs[i] == local_slice_high.max():
            pivot_highs.append((dates[i], highs[i]))

    return pivot_lows, pivot_highs


# =====================================================
# 3) Basin Detection (Sideways Accumulation/Distribution)
# =====================================================
def detect_basins(df, window=5, std_threshold=0.015):
    closes = df['Close']
    basins = []

    for i in range(0, len(df) - window):
        segment = closes.iloc[i:i + window]

        # Low volatility = flat region
        if segment.std() / segment.mean() < std_threshold:
            center_price = segment.mean()
            basins.append((segment.index[0], center_price))

    return basins


# =====================================================
# 4) Touchpoint Clustering (supports/resistances)
# =====================================================
def cluster_levels(levels, eps_pct=0.02, min_samples=2):
    if len(levels) == 0:
        return []

    prices = np.array([x[1] for x in levels]).reshape(-1, 1)

    eps_value = np.mean(prices) * eps_pct

    clustering = DBSCAN(eps=eps_value, min_samples=min_samples).fit(prices)
    labels = clustering.labels_

    clusters = []
    for cluster_id in set(labels):
        if cluster_id == -1:
            continue  # ignore noise

        cluster_points = [(levels[i][0], levels[i][1]) for i in range(len(levels)) if labels[i] == cluster_id]

        avg_price = np.mean([p[1] for p in cluster_points])
        first_date = min([p[0] for p in cluster_points])

        clusters.append({
            "date": str(first_date.date()),
            "price": round(float(avg_price), 2),
            "touches": len(cluster_points),
            "type": "cluster"
        })

    return clusters


# =====================================================
# 5) Build Zone (±2.5%)
# =====================================================
def build_zone(price):
    return (
        round(price * 0.975, 2),
        round(price * 1.025, 2)
    )


# =====================================================
# 6) Filter by 14–17% spacing rule
# =====================================================
def filter_spacing(levels):
    levels = sorted(levels, key=lambda x: x["price"], reverse=True)

    final = []
    last_price = None

    for lvl in levels:
        price = lvl["price"]

        if last_price is None:
            final.append(lvl)
            last_price = price
            continue

        gap_pct = abs(price - last_price) / last_price * 100

        if 14 <= gap_pct <= 17:
            final.append(lvl)
            last_price = price

    return final


# =====================================================
# 7) Main Detection Function
# =====================================================
def detect_supports(df_daily):
    """
    FINAL EXPOSED FUNCTION
    Combines:
    - Pivot lows (support)
    - Pivot highs (resistance)
    - Basins
    - Clusters
    - Spacing rule
    """

    df = resample_to_weekly(df_daily)

    pivot_lows, pivot_highs = detect_improved_pivots(df)
    basins = detect_basins(df)

    # Tag pivot types
    pivot_low_items = [{"date": str(d.date()), "price": float(p), "type": "pivot"} for d, p in pivot_lows]
    pivot_high_items = [{"date": str(d.date()), "price": float(p), "type": "pivot"} for d, p in pivot_highs]
    basin_items = [{"date": str(d.date()), "price": float(p), "type": "basin"} for d, p in basins]

    # Combine all candidate levels
    all_levels = pivot_low_items + pivot_high_items + basin_items

    # Build clustering input
    cluster_input = [(pd.to_datetime(l["date"]), l["price"]) for l in all_levels]
    clusters = cluster_levels(cluster_input)

    # Combine pivots + basins + clusters
    merged = all_levels + clusters

    # De-duplicate by price proximity
    merged = sorted(merged, key=lambda x: x["price"])
    deduped = []
    for lvl in merged:
        if len(deduped) == 0:
            deduped.append(lvl)
        else:
            if abs(lvl["price"] - deduped[-1]["price"]) / deduped[-1]["price"] > 0.01:
                deduped.append(lvl)

    # Apply spacing filter
    spaced = filter_spacing(deduped)

    # Build zones
    for lvl in spaced:
        zl, zh = build_zone(lvl["price"])
        lvl["zone_low"] = zl
        lvl["zone_high"] = zh

    # Sort final output
    spaced = sorted(spaced, key=lambda x: x["price"], reverse=True)

    return spaced
