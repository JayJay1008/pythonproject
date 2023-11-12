import time
import hmac
import hashlib
import requests

BASE_URL = "https://api.binance.com"


class BinanceAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.transactions = []  # Store the transactions here

    def _get_signature(self, data):
        return hmac.new(bytes(self.api_secret, 'latin-1'), msg=bytes(data, 'latin-1'),
                        digestmod=hashlib.sha256).hexdigest()

    def get_symbol_info(self, symbol):
        headers = {
            "X-MBX-APIKEY": self.api_key
        }

        response = requests.get(f"{BASE_URL}/api/v3/exchangeInfo", headers=headers, params={"symbol": symbol})

        return response.json()

    def get_balance(self):
        timestamp = int(time.time() * 1000)
        data = f"timestamp={timestamp}"

        headers = {
            "X-MBX-APIKEY": self.api_key
        }

        signature = self._get_signature(data)
        response = requests.get(f"{BASE_URL}/api/v3/account", headers=headers, params=data + f"&signature={signature}")

        balances = {}
        for asset in response.json().get("balances", []):
            if float(asset["free"]) > 0 or float(asset["locked"]) > 0:
                balances[asset["asset"]] = {
                    "free": asset["free"],
                    "locked": asset["locked"]
                }
        return balances
    def _send_order(self, symbol, side, quantity, price, order_type="LIMIT"):
        timestamp = int(time.time() * 1000)  # Binance uses milliseconds timestamp
        data = f"symbol={symbol}&side={side}&type={order_type}&timeInForce=GTC&quantity={quantity}&price={price}&timestamp={timestamp}"

        headers = {
            "X-MBX-APIKEY": self.api_key
        }

        signature = self._get_signature(data)
        response = requests.post(f"{BASE_URL}/api/v3/order", headers=headers, data=data + f"&signature={signature}")
        print(side)
        print(response.content)
        # Log the transaction after sending an order
        self.transactions.append({
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "timestamp": timestamp,
            "response": response.json()
        })

        return response.json()

    def buy(self, symbol, quantity, price):
        return self._send_order(symbol, "BUY", quantity, price)

    def sell(self, symbol, quantity, price):
        return self._send_order(symbol, "SELL", quantity, price)

    def view_transactions(self):
        return self.transactions

# Usage:
# api = BinanceAPI(YOUR_API_KEY, YOUR_API_SECRET)
# buy_response = api.buy("BTCUSDT", 1, 40000)
# sell_response = api.sell("BTCUSDT", 1, 45000)
# transactions = api.view_transactions()
# print(transactions)
