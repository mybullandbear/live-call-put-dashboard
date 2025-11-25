import os

# Fyers API Credentials (get from https://myapi.fyers.in/dashboard)
FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
FYERS_CLIENT_SECRET = os.getenv('FYERS_CLIENT_SECRET', 'YOUR_SECRET_HERE')
REDIRECT_URI = 'http://localhost:5000/auth/callback'  # For OAuth

# App Config
APP_SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-me')
DEBUG = True

# Default Symbols & Expiry (NSE weekly/monthly)
DEFAULT_SYMBOL = 'NSE:NIFTY50-INDEX'  # Underlying
SYMBOLS = {
    'NIFTY': 'NSE:NIFTY50-INDEX',
    'BANKNIFTY': 'NSE:NSEBANK-INDEX',
    'FINNIFTY': 'NSE:FINNIFTY-INDEX'
}