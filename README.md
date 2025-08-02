# marketDataAgent

A small FastAPI service that returns real-time stock prices from Yahoo Finance.

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn app:app --reload --port 8000
```

## Endpoints

- `POST /price` – request body `{ "symbol": "AAPL" }` returns latest price
- `GET /.well-known/agent.json` – returns the agent card used for discovery

## Example

```bash
curl -X POST "http://localhost:8000/price" -H "Content-Type: application/json" -d '{"symbol": "AAPL"}'
curl http://localhost:8000/.well-known/agent.json
```
