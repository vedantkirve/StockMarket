# app/controllers/analysis_controller.py

from app.services.strategy_service import analyze_stock

def analyze_controller(symbol: str):
    return analyze_stock(symbol)
