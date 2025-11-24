# app/main.py

from fastapi import FastAPI
from app.routes.analysis_routes import router as analysis_router
from app.routes.candles_routes import router as candles_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api")
app.include_router(candles_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Trading System API is running"}
