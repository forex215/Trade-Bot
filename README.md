# XAUUSD AI Scalping Bot (Paper Trading)

Aggressive full-stack learning bot for Gold (XAUUSD) with FastAPI backend + React/Tailwind frontend.

## Important Reality Check (85% Win Rate)

- An **85% live win rate is not guaranteed** in real markets.
- What you can target instead: disciplined risk controls, high-quality data, strict session filtering, and continuous retraining/evaluation.
- Use this project as a **free training + paper-trading framework** to measure if your strategy can approach your target on out-of-sample data.

## What You Need (Free Stack)

1. Python 3.11+
2. Node.js 20+
3. Free data source (Yahoo Finance endpoint used in project)
4. SQLite (built-in)
5. Optional Telegram bot for alerts
6. Render/Railway (backend) + Vercel (frontend)

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
- `POST /train` → retrain ML model and return current metrics
- `WS /ws/price` → real-time streaming price + signal payload

## Frontend Setup (React + Tailwind)

1. `cd frontend`
2. `npm install`
3. `echo "VITE_API_URL=http://localhost:8000" > .env`
4. Optional websocket override:
   - `echo "VITE_WS_URL=ws://localhost:8000/ws/price" >> .env`
5. `npm run dev`
6. Open http://localhost:5173

## Strategy Logic (Aggressive, Low HOLD)

- BUY primary trigger: `RSI < 35` + MACD bullish crossover
- SELL primary trigger: `RSI > 65` + MACD bearish crossover
- HOLD reduction: loosened bias thresholds (`RSI < 38` or bullish crossover, `RSI > 62` or bearish crossover)
- ML gate: RandomForest / LogisticRegression probability on RSI/MACD/EMA/returns/ATR/volatility
- Trade executes when confidence > 65% (or strong override)
- Profit handling:
  - Target quick booking near +$10
  - Move stop to break-even after +$5

## Training Plan to Push Accuracy Higher

1. Gather at least 3-6 months of 1m/5m data.
2. Train daily with walk-forward validation (never random split for time series).
3. Keep only high-confidence predictions (e.g., > 0.70).
4. Add features: ATR, volatility, session, spread bucket, candle patterns.
5. Measure precision and win-rate separately for BUY and SELL.
6. Retune threshold weekly using only recent out-of-sample data.

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
