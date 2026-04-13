# XAUUSD AI Scalping Bot (MT5 + Local Data + Timeframe Planning)

## Key fixes included
- UI text visibility fixed (high-contrast colors).
- Buttons are wired to backend APIs (`/trade`, `/train`, `/autotrade`, `/history`).
- Realtime stream restored using `/ws/price`.
- If MT5 is unavailable, app replays data from `Data/*.csv` for live simulation.
- Training now prioritizes your local dataset in `Data/`.
- Added timeframe-aware planning endpoint: `GET /plan?timeframes=15m,1h`.

## Data folder
Put your downloaded XAUUSD CSV files in:

```text
Trade-Bot/Data/
```

Supported columns (case-insensitive variants accepted):
- timestamp/time/datetime/date
- open, high, low, close
- volume (optional)

## Run backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Run frontend
```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

## Main APIs
- `GET /price`
- `GET /signal?timeframe=15m`
- `GET /plan?timeframes=5m,15m,1h`
- `POST /trade`
- `POST /close`
- `GET /history`
- `POST /train`
- `GET/POST /autotrade`
- `WS /ws/price`
