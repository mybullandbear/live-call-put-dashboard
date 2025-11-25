# Live Call vs Put Dashboard

Replicates TradingTick's Call vs Put page with live Fyers data.

## Setup
1. `pip install -r requirements.txt`
2. Set env: `export FYERS_CLIENT_ID=xxx` & `FYERS_CLIENT_SECRET=yyy`
3. `python app.py`
4. Visit localhost:5000 → Auth → Select symbol/expiry.

## Customization
- Add WS: Extend `fyers_client.subscribe_live()` for true real-time.
- Expiries: Integrate `fyers.get_expiry_dates()`.
- Deploy: Heroku/Vercel (use ngrok for webhooks if needed).

Built with Flask, Fyers API, Plotly.