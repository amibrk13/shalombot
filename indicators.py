import requests
import pandas as pd
import numpy as np
import ta
import os
from datetime import datetime

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")

HEADERS = {
    "X-BYBIT-API-KEY": BYBIT_API_KEY
}

# Таймфреймы
TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D"
}

# Запрос свечей с Bybit
def fetch_ohlcv(symbol: str, interval: str, limit: int = 200):
    url = "https://api.bybit.com/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()
    
    if "result" not in data or "list" not in data["result"]:
        raise ValueError("Invalid response from Bybit")

    ohlcv = pd.DataFrame(data["result"]["list"])
    ohlcv.columns = ["timestamp", "open", "high", "low", "close", "volume", "_"]
    ohlcv = ohlcv[["timestamp", "open", "high", "low", "close", "volume"]].astype(float)
    ohlcv["timestamp"] = pd.to_datetime(ohlcv["timestamp"], unit="ms")
    ohlcv = ohlcv.sort_values("timestamp").reset_index(drop=True)
    
    return ohlcv

# Вычисление индикаторов
def compute_indicators(df):
    close = df["close"]
    volume = df["volume"]

    ema_50 = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]
    ema_200 = ta.trend.EMAIndicator(close, window=200).ema_indicator().iloc[-1]
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]

    stoch = ta.momentum.StochRSIIndicator(close, window=14, smooth1=3, smooth2=3)
    stoch_k = stoch.stochrsi_k().iloc[-1]
    stoch_d = stoch.stochrsi_d().iloc[-1]

    return {
        "close": round(close.iloc[-1], 10),
        "ema_50": round(ema_50, 10),
        "ema_200": round(ema_200, 10),
        "rsi": round(rsi, 2),
        "stoch_rsi_k": round(stoch_k, 2),
        "stoch_rsi_d": round(stoch_d, 2),
        "volume": round(volume.iloc[-1], 2),
    }

# Анализ по всем таймфреймам
def compute_indicators_for_all_timeframes(symbol: str):
    result = {}
    for name, interval in TIMEFRAMES.items():
        df = fetch_ohlcv(symbol, interval)
        indicators = compute_indicators(df)
        result[name] = indicators
    return result
