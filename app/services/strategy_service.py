# app/services/strategy_service.py

# from app.services.support_service import detect_supports
from app.services.rsi_service import compute_rsi_support
from app.services.fibonacci_service import compute_fibonacci_levels
from app.services.candle_service import fetch_candles
from app.services.support_service import detect_supports
import os

def analyze_stock(symbol: str, include_df: bool = False):
    df = fetch_candles(symbol, period="10y", timeframe="1D")

        # ----------------------------
    # Save CSV for debugging
    # ----------------------------
    # data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    # os.makedirs(data_dir, exist_ok=True)

    # csv_path = os.path.join(data_dir, f"{symbol.replace('.', '_')}.csv")

    # df.to_csv(csv_path, index=True)
    # print(f"Saved CSV to: {csv_path}")
    # ----------------------------

    result = {"symbol": symbol}

    # Conditional raw DF
    if include_df:
        df_fixed = df.reset_index()
        df_fixed["Date"] = df_fixed["Date"].dt.strftime("%Y-%m-%d")   # <-- FIX HERE

        result["df_data"] = df_fixed[["Date", "Open", "High", "Low", "Close"]].rename(
            columns={
                "Date": "time",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close"
            }
        ).to_dict(orient="records")
    # Always include these
    result["supports"] = detect_supports(df.copy())
    result["rsi"] = compute_rsi_support(df.copy())
    result["fibonacci"] = compute_fibonacci_levels(df.copy())

    # Final scoring
    score = 0
    if len(result["supports"]) > 0:
        score += 1
    if result["rsi"]["is_rsi_support"]:
        score += 1
    if result["fibonacci"]["fib_hit"] is not None:
        score += 1

    result["final_signal"] = "BUY" if score >= 2 else "WAIT"

    return result
