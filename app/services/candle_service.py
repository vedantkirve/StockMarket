import yfinance as yf
import pandas as pd


def fetch_candles(symbol: str, period="10y", timeframe="1D"):
    """
    Always fetch DAILY candles for accuracy.
    Weekly candles will be computed manually.
    """

    interval = "1d"  # Always daily

    df = yf.download(symbol, period=period, interval=interval)

    if df is None or df.empty:
        return pd.DataFrame()

    df.dropna(inplace=True)

    # Fix MultiIndex bug
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    return df
