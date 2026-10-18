# AlphaFlow — Python Trading Platform

```bash
# Backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
# API docs: http://localhost:8000/api/docs

# Frontend
cd frontend && npm install && npm run dev
# UI: http://localhost:5173

# Tests
pytest tests/
black backend/ core/ && flake8 backend/ core/ && mypy backend/ core/
```

**Architecture:** `core/` is the trading engine (strategy logic, backtester, risk manager, indicators). `backend/` is the FastAPI layer with REST endpoints. `frontend/src/pages/` has 6 pages (Dashboard, Trading, Strategies, Analytics, Backtest, Settings).
