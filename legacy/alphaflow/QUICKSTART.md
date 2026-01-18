# ⚡ AlphaFlow Quick Start Guide

Get AlphaFlow running in **5 minutes**!

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Alpaca API keys ([Get them free](https://alpaca.markets))

## 🚀 Installation

### 1. Install Dependencies

```bash
# Backend
pip install -r requirements-backend.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Configure API Keys

```bash
# Copy template
cp .env.example .env

# Add your Alpaca keys to .env file
```

### 3. Start the Application

Open **two terminals**:

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm run dev
```

### 4. Open Browser

Go to: **http://localhost:3000**

## ✅ You're Done!

You should see:
- ✅ Dashboard with portfolio metrics
- ✅ Watchlist with live quotes
- ✅ Professional Bloomberg-style UI
- ✅ Clean, modern interface

## 🎯 Next Steps

1. **Explore the Dashboard** - See your portfolio overview
2. **Check the API Docs** - Visit http://localhost:8000/api/docs
3. **Try Backtesting** - Test a strategy
4. **Read the Docs** - See README.md for full features

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Try manual start
python3 -m uvicorn backend.main:app --reload
```

### Frontend won't start?
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Can't see data?
- Make sure both servers are running
- Check browser console for errors
- Verify Alpaca API keys in `.env`

## 📚 Learn More

- **Full Documentation**: README.md
- **Migration Guide**: MIGRATION_GUIDE.md
- **API Reference**: http://localhost:8000/api/docs

---

**Happy Trading!** 📈
