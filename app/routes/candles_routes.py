from fastapi import APIRouter
from app.controllers.candles_controller import get_candles_controller

router = APIRouter()

@router.get("/candles")
def get_candles(symbol: str):
    """
    Fetch daily OHLC candle data for a given stock symbol
    Example: /api/candles?symbol=RELIANCE.NS
    """
    return get_candles_controller(symbol)
