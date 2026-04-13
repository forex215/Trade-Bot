# XAUUSD AI Scalping Bot (Paper Trading)

Aggressive full-stack learning bot for Gold (XAUUSD) with FastAPI backend + React/Tailwind frontend.

## Folder Structure

```
Trade-Bot/
├── backend/
│   ├── app/
│   │   ├── backtesting.py
│   │   ├── config.py
│   │   ├── data_provider.py
│   │   ├── indicators.py
│   │   ├── logger.py
│   │   ├── main.py
│   │   ├── ml_model.py
│   │   ├── models.py
│   │   ├── patterns.py
│   │   ├── sessions.py
│   │   ├── strategy.py
│   │   ├── telegram_alerts.py
│   │   └── trading.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PriceChart.jsx
│   │   │   ├── SignalCard.jsx
│   │   │   ├── TradeControls.jsx
│   │   │   └── TradeHistory.jsx
│   │   ├── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
└── README.md
```

## Backend Setup (FastAPI)

1. `cd backend`
2. `python -m venv .venv`
3. `source .venv/bin/activate` (Windows: `.venv\\Scripts\\activate`)
4. `pip install -r requirements.txt`
5. `cp .env.example .env` and edit values
6. Start API:
   - `uvicorn app.main:app --reload --port 8000`

### Backend Endpoints
- `GET /price` → live/simulated XAUUSD price + spread
- `GET /signal` → BUY/SELL/HOLD + confidence + win/lose probability
- `POST /trade` → open paper trade (auto or forced side)
- `POST /close` → manually close active trade
- `GET /history` → trade logs from SQLite
- `GET /backtest` → simple strategy backtest summary

## Frontend Setup (React + Tailwind)

1. `cd frontend`
2. `npm install`
3. `echo "VITE_API_URL=http://localhost:8000" > .env`
4. `npm run dev`
5. Open http://localhost:5173

## Strategy Logic (Aggressive, Low HOLD)

- BUY primary trigger: `RSI < 35` + MACD bullish crossover
- SELL primary trigger: `RSI > 65` + MACD bearish crossover
- HOLD reduction: loosened bias thresholds (`RSI < 38` or bullish crossover, `RSI > 62` or bearish crossover)
- ML gate: RandomForest probability on RSI/MACD/EMA/returns
- Trade executes when confidence > 65% (or strong override)
- Profit handling:
  - Target quick booking near +$10
  - Move stop to break-even after +$5

## Risk Management

- Fixed configurable lot size + quantity
- Approx 1:2 stop-loss : take-profit ratio
- Blocks entries on high spread
- Trades only London/New York UTC session overlap windows

## Bonus Features Included

- Telegram alerts for open/close events (optional token/chat id)
- Backtesting endpoint
- Candlestick confirmation (engulfing pattern)

## Free Deployment

### Backend on Render/Railway
- Deploy `backend/` as Python web service
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add env vars from `.env.example`

### Frontend on Vercel
- Import `frontend/` as Vite project
- Build: `npm run build`
- Output: `dist`
- Set `VITE_API_URL` to deployed backend URL

## Notes
- This is paper trading only (no real broker execution).
- For real MT5 integration, swap `DataProvider` with MetaTrader5 package feed and authenticated order routing.
