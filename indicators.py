import requests
import pandas as pd
import ta

# --- НАСТРОЙКИ ---
API_KEY = "r7wZmhKJ2orE1dVqZM"
API_SECRET = "n0QB6JyDSc9K6icWJSOLszKU2EGWThkfkKVG"
BASE_URL = "https://api.bybit.com"
HEADERS = {"X-BYBIT-API-KEY": API_KEY}

TIMEFRAMES = {
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D"
}

LIMIT = 200  # максимум, доступный по API

def fetch_ohlcv(symbol: str, interval: str):
    url = f"{BASE_URL}/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": LIMIT
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data["retCode"] != 0:
        raise ValueError(f"API Error: {data['retMsg']}")

    df = pd.DataFrame(data["result"]["list"])
    df.columns = [
        "timestamp", "open", "high", "low", "close", "volume", "turnover"
    ]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df

def calculate_indicators(df: pd.DataFrame):
    result = {}
    result["close"] = df["close"].iloc[-1]
    result["volume"] = df["volume"].iloc[-1]
    result["ema_50"] = ta.trend.ema_indicator(df["close"], window=50).iloc[-1]
    result["ema_200"] = ta.trend.ema_indicator(df["close"], window=200).iloc[-1]
    result["rsi"] = ta.momentum.rsi(df["close"], window=14).iloc[-1]
    
    stoch_rsi = ta.momentum.stochrsi(df["close"], window=14, smooth1=3, smooth2=3)
    result["stoch_rsi"] = stoch_rsi.iloc[-1]
    
    return result

def compute_indicators_for_all_timeframes(symbol: str):
    all_data = {}
    for label, interval in TIMEFRAMES.items():
        df = fetch_ohlcv(symbol, interval)
        indicators = calculate_indicators(df)
        all_data[label] = indicators
    return all_data
