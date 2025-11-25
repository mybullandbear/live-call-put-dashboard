from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from config import FYERS_CLIENT_ID, FYERS_CLIENT_SECRET, REDIRECT_URI, APP_SECRET_KEY, SYMBOLS, DEFAULT_SYMBOL
from fyers_client import FyersClient
from data_processor import process_chain_data, create_plots
import threading
import time
from datetime import datetime

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
app.config['DEBUG'] = True

# Global client (thread-safe)
fyers_client = None
data_cache = {'df': None, 'ratios': {}, 'timestamp': None}
cache_lock = threading.Lock()

def update_data():
    """Background thread for polling live data."""
    global data_cache
    while True:
        if fyers_client and fyers_client.access_token:
            symbol = request.form.get('symbol', DEFAULT_SYMBOL) if request else DEFAULT_SYMBOL
            expiry = request.form.get('expiry', get_next_expiry()) if request else get_next_expiry()
            df_raw = fyers_client.get_option_chain(symbol, expiry)
            with cache_lock:
                data_cache['df'], data_cache['ratios'] = process_chain_data(df_raw)
                data_cache['timestamp'] = datetime.now().isoformat()
        time.sleep(30)  # Poll every 30s

def get_next_expiry():
    """Simple: Next Thursday for weekly (customize)."""
    return "25-11-2025"  # Placeholder; fetch dynamically via API

@app.route('/')
def index():
    return render_template('index.html', symbols=SYMBOLS)

@app.route('/auth')
def auth():
    if not FYERS_CLIENT_ID or FYERS_CLIENT_ID == 'YOUR_CLIENT_ID_HERE':
        return "Set FYERS_CLIENT_ID in env!", 500
    global fyers_client
    fyers_client = FyersClient(FYERS_CLIENT_ID, FYERS_CLIENT_SECRET, REDIRECT_URI)
    auth_url = fyers_client.generate_auth_url()
    return redirect(auth_url)

@app.route('/auth/callback')
def callback():
    global fyers_client
    code = request.args.get('auth_code')
    if fyers_client.set_access_token(code):
        # Start background updater
        threading.Thread(target=update_data, daemon=True).start()
        session['authenticated'] = True
        return redirect(url_for('index'))
    return "Auth failed!", 500

@app.route('/data', methods=['POST'])
def get_data():
    if not session.get('authenticated'):
        return jsonify({'error': 'Authenticate first'}), 401
    
    symbol = request.form['symbol']
    expiry = request.form['expiry']
    df_raw = fyers_client.get_option_chain(symbol, expiry)
    df, ratios = process_chain_data(df_raw)
    oi_json, pcr_json, table_json = create_plots(df, ratios)
    
    return jsonify({
        'data': df.to_dict('records'),
        'ratios': ratios,
        'plots': {'oi': oi_json, 'pcr': pcr_json, 'table': table_json},
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)