# app/services/strategy_service.py

# from app.services.support_service import detect_supports
from app.services.rsi_service import compute_rsi_support
from app.services.fibonacci_service import compute_fibonacci_levels
from app.services.candle_service import fetch_candles
from app.services.support_service import detect_supports
import os

def analyze_stock(symbol: str):
    df = fetch_candles(symbol, period="5y", timeframe="1D")

        # ----------------------------
    # Save CSV for debugging
    # ----------------------------
    # data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    # os.makedirs(data_dir, exist_ok=True)

    # csv_path = os.path.join(data_dir, f"{symbol.replace('.', '_')}.csv")

    # df.to_csv(csv_path, index=True)
    # print(f"Saved CSV to: {csv_path}")
    # ----------------------------

    supports = detect_supports(df)
    rsi_info = compute_rsi_support(df)
    fib_info = compute_fibonacci_levels(df)

    # Final signal (simple logic for now)
    score = 0
    if len(supports) > 0:
        score += 1
    if rsi_info["is_rsi_support"]:
        score += 1
    if fib_info["fib_hit"] is not None:
        score += 1

    if score >= 2:
        final_signal = "BUY"
    else:
        final_signal = "WAIT"

    return {
        "symbol": symbol,
        "supports": supports,
        "rsi": rsi_info,
        "fibonacci": fib_info,
        "final_signal": final_signal
    }
