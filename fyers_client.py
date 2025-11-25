from fyers_apiv3 import fyersModel
import json
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FyersClient:
    def __init__(self, client_id, secret, redirect_uri):
        self.client_id = client_id
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.session = fyersModel.SessionModel(client_id=client_id, secret_key=secret, redirect_uri=redirect_uri, response_type="code", grant_type="authorization_code")
        self.access_token = None
        self.fyers = None

    def generate_auth_url(self):
        return self.session.generate_authcode()

    def set_access_token(self, auth_code):
        session = self.session.generate_token(auth_code)
        if session['s'] == 'ok':
            self.access_token = session['access_token']
            self.fyers = fyersModel.FyersModel(client_id=self.client_id, token=self.access_token, log_path="")  # No logs for prod
            logger.info("Auth successful!")
            return True
        return False

    def get_option_chain(self, symbol, expiry):
        """Fetch option chain for calls & puts around ATM."""
        try:
            # Get underlying price
            data = self.fyers.quotes({"symbols": symbol})
            underlying_price = data['d'][0]['v']['lp']  # Last Price

            # Strikes: ATM ± 10 (adjust for range)
            atm_strike = round(underlying_price / 50) * 50  # NIFTY step 50
            strikes = [atm_strike - (i * 50) for i in range(5, 0, -1)] + [atm_strike + (i * 50) for i in range(1, 6)]

            chain_data = []
            for strike in strikes:
                # Call option symbol
                call_symbol = f"NSE:{symbol.split(':')[1].replace('-INDEX', '')}{expiry.replace('-', '')}CE{strike}"
                call_data = self.fyers.quotes({"symbols": call_symbol})
                if call_data['s'] == 'ok' and call_data['d']:
                    chain_data.append({
                        'strike': strike,
                        'type': 'Call',
                        'ltp': call_data['d'][0]['v']['lp'],
                        'volume': call_data['d'][0]['v']['volume'],
                        'oi': call_data['d'][0]['v']['oi']
                    })

                # Put option symbol
                put_symbol = f"NSE:{symbol.split(':')[1].replace('-INDEX', '')}{expiry.replace('-', '')}PE{strike}"
                put_data = self.fyers.quotes({"symbols": put_symbol})
                if put_data['s'] == 'ok' and put_data['d']:
                    chain_data.append({
                        'strike': strike,
                        'type': 'Put',
                        'ltp': put_data['d'][0]['v']['lp'],
                        'volume': put_data['d'][0]['v']['volume'],
                        'oi': put_data['d'][0]['v']['oi']
                    })

            df = pd.DataFrame(chain_data)
            return df
        except Exception as e:
            logger.error(f"Error fetching chain: {e}")
            return pd.DataFrame()

    def subscribe_live(self, symbols):
        """Subscribe to WebSocket for live updates (calls on_data callback)."""
        try:
            self.fyers.websocket_data("Subscribe", symbols, "0")
            self.fyers.subscribe_data()
        except Exception as e:
            logger.error(f"WebSocket error: {e}")