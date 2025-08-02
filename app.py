import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf


logger = logging.getLogger("market_data_bot")
logging.basicConfig(level=logging.INFO)

app = FastAPI()


class PriceRequest(BaseModel):
    symbol: str


@app.post("/price")
async def get_price(req: PriceRequest):
    symbol = req.symbol
    ticker = yf.Ticker(symbol)
    price = ticker.info.get("regularMarketPrice")
    logger.info("MarketDataBot: %s price is %s", symbol, price)
    if price is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return {"symbol": symbol, "price": price}


@app.get("/.well-known/agent.json")
async def agent_card():
    agent_path = Path(__file__).parent / ".well-known" / "agent.json"
    try:
        with agent_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="agent.json not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid agent.json")
