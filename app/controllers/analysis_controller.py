# app/controllers/analysis_controller.py

from app.services.strategy_service import analyze_stock

def analyze_controller(symbol: str, include_df: bool = False):
    return analyze_stock(symbol, include_df)
