import httpx
import pandas as pd
import numpy as np
import ta
import os

from dotenv import load_dotenv
load_dotenv()

# API keys
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

# Таймфреймы и интервалы Bybit
TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D"
}

# Получить OHLCV через Bybit API v5
async def fetch_ohlcv(symbol: str, interval: str, limit: int = 200):
    url = "https://api.bybit.com/v5/market/kline"
    headers = {
        "X-BYBIT-API-KEY": API_KEY
    }
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        data = response.json()
        if "result" not in data or "list" not in data["result"]:
            raise ValueError(f"Invalid response for {symbol}: {data}")
        df = pd.DataFrame(data["result"]["list"])
        df.columns = ["timestamp", "open", "high", "low", "close", "volume", "turnover"]
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
        df = df.astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

# Тех. индикаторы
def compute_indicators(df):
    close = df["close"]
    volume = df["volume"]

    ema_50 = ta.trend.ema_indicator(close, window=50).ema_indicator().iloc[-1]
    ema_200 = ta.trend.ema_indicator(close, window=200).ema_indicator().iloc[-1]
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
        "volume": round(volume.iloc[-1], 2)
    }

# Главный анализатор
async def compute_indicators_for_all_timeframes(symbol: str):
    result = {}
    for tf_name, interval in TIMEFRAMES.items():
        df = await fetch_ohlcv(symbol, interval)
        result[tf_name] = compute_indicators(df)
    return result
