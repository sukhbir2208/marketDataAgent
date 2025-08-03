import asyncio
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import yfinance as yf


logger = logging.getLogger("market_data_bot")
logging.basicConfig(level=logging.INFO)

app = FastAPI()


class PriceRequest(BaseModel):
    """Request model for the /price endpoint."""

    symbol: str = Field(
        ..., pattern=r"^[A-Z]{1,5}$", description="Ticker symbol, 1-5 uppercase letters"
    )


class PriceResponse(BaseModel):
    """Response model for the /price endpoint."""

    symbol: str
    price: float


@lru_cache(maxsize=256)
def _fetch_price(symbol: str) -> Optional[float]:
    """Fetch the latest price for *symbol* using yfinance."""

    ticker = yf.Ticker(symbol)
    try:
        price = ticker.fast_info.get("lastPrice")
        if price is None:
            price = ticker.info.get("regularMarketPrice")
    except Exception:
        logger.exception("Failed to fetch price for %s", symbol)
        return None
    return price


@app.post("/price", response_model=PriceResponse)
async def get_price(req: PriceRequest) -> PriceResponse:
    """Return the latest market price for the requested symbol."""

    symbol = req.symbol
    loop = asyncio.get_running_loop()
    price = await loop.run_in_executor(None, _fetch_price, symbol)
    logger.info("MarketDataBot: %s price is %s", symbol, price)
    if price is None:
        raise HTTPException(status_code=404, detail="Symbol not found")
    return PriceResponse(symbol=symbol, price=price)


@app.get("/.well-known/agent.json")
async def agent_card() -> dict:
    """Serve the agent metadata for discovery."""

    agent_path = Path(__file__).parent / ".well-known" / "agent.json"
    try:
        with agent_path.open() as f:
            return json.load(f)
    except FileNotFoundError:
        logger.exception("agent.json not found at %s", agent_path)
        raise HTTPException(status_code=404, detail="agent.json not found")
    except json.JSONDecodeError:
        logger.exception("agent.json at %s is invalid JSON", agent_path)
        raise HTTPException(status_code=500, detail="Invalid agent.json")
