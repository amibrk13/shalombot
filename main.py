from fastapi import FastAPI
from indicators import compute_indicators_for_all_timeframes

app = FastAPI()

@app.get("/analyze/{symbol}")
def analyze_symbol(symbol: str):
    try:
        result = compute_indicators_for_all_timeframes(symbol)
        return result
    except Exception as e:
        return {"error": str(e)}
