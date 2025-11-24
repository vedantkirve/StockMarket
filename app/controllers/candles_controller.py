from app.services.candle_service import fetch_candles

def get_candles_controller(symbol: str):
    """
    Controller layer:
    - Receive request from router
    - Call service
    - Format clean response
    """
    df = fetch_candles(symbol)

    # Convert DataFrame → JSON-friendly objects
    data = df.reset_index().to_dict(orient="records")

    return {
        "symbol": symbol,
        "count": len(data),
        "data": data
    }
