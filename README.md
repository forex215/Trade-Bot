# XAUUSD AI Scalping Bot (Paper Trading, MT5 + News Filter)

Aggressive full-stack learning bot for Gold (XAUUSD) using FastAPI backend + React/Tailwind frontend.

## What Changed (Requested)

- MT5 is mandatory for real-time price and OHLC data (no realtime fallback).
- Model training now uses last 10 years of XAUUSD data (`/train`) via MT5 H1 candles (Yahoo fallback only if MT5 unavailable).
- News-aware filter blocks trading during high-impact ForexFactory news windows.
- Auto-trading executes only when confidence >= 75%.
- Auto-trading can be enabled/disabled from API and frontend toggle.

## Setup Prerequisites

1. Python 3.11+
2. Node.js 20+
3. MetaTrader 5 terminal installed and logged in to a broker account with XAUUSD enabled
4. Internet access for ForexFactory XML calendar

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
echo "VITE_WS_URL=ws://localhost:8000/ws/price" >> .env
npm run dev
```

Open: http://localhost:5173

> If MT5 is not connected/logged in with XAUUSD symbol enabled, realtime endpoints will return HTTP 503.

## API Endpoints

- `GET /price`
- `GET /signal`
- `POST /trade`
- `POST /close`
- `GET /history`
- `GET /backtest`
- `POST /train` (10-year training run)
- `GET /autotrade` and `POST /autotrade`
- `WS /ws/price`

## Notes

- This remains paper-trading logic; you can wire real MT5 order execution later.
- 85% win-rate cannot be guaranteed in live market conditions.


## UI Template

- The app now renders your provided premium dashboard UI via `frontend/public/dashboard.html` inside the React shell.
