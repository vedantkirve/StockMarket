# app/routes/analysis_routes.py

from fastapi import APIRouter
from app.controllers.analysis_controller import analyze_controller

router = APIRouter()

@router.get("/analyze")
def analyze(symbol: str, include_df: bool = False):
    return analyze_controller(symbol, include_df)
