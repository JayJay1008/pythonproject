import requests
import time
import datetime
import json
import csv
import sys
from termcolor import colored
from binance_api import BinanceAPI
import os




api = BinanceAPI(api_key="2pV9yLM5LctY4CkCPWEUZj4NeLWqymkCSGmYfsVWjMiIEZzebPs0QYbmGKpf7NOI",
                 api_secret="whFXu8Qfyl01YApibxpJgeQBsI7UUwjl2LChsKgAKVZRFy91KHis9lKg93CYd8YN")

# Define your initial_prices dictionary here, for example:
initial_prices = {
    "storj": 0.230516,
}
number_of_tokens = {
    "storj": 1,
}

symbols = {
   "storj": "STORJUSDT",  # Assuming the symbol for quiztok in Euro is QTCONEUR, you might want to verify this.
}
tick_size= {
    "storj": "0.00010000",
}
import requests
import time

# Cache expiration time (e.g., 1 hour)
CACHE_EXPIRATION = 36000

# Cache data structure
cache = {
    "symbols": [],
    "timestamp": 0
}


def fetch_symbols_from_binance():
    response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
    data = response.json()
    symbols = [pair['symbol'] for pair in data['symbols']]
    return symbols

def get_cached_symbols():
    # If cache is empty or expired, fetch new data
    current_time = time.time()
    if not cache['symbols'] or (current_time - cache['timestamp'] > CACHE_EXPIRATION):
        cache['symbols'] = fetch_symbols_from_binance()
        cache['timestamp'] = current_time
    return cache['symbols']

def check_symbol_validity(symbol_to_check):
    symbols = get_cached_symbols()
    if symbol_to_check in symbols:
        print(f"{symbol_to_check} is a valid trading pair on Binance.")
    else:
        print(f"{symbol_to_check} is NOT a valid trading pair on Binance.")
        # sys.exit(1)
check_symbol_validity("BTCV")

def get_coin_id(coin_name):
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        coins = response.json()
        for coin in coins:
            if coin_name.lower() in coin['name'].lower():
                return coin['id']
    return None

# bomb_id = get_coin_id("BOMB")
# print(bomb_id)

os.environ['TERM'] = 'xterm'
def supports_colors():
    return True

def supports_colors2():
    supported_platform = sys.platform != 'Pocket PC'
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True

def write_to_csv(row):
    with open('/Users/jayananda/Documents/crypto/bitcoin_prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

if not os.path.exists('/Users/jayananda/Documents/crypto/bitcoin_prices.csv'):
    with open('/Users/jayananda/Documents/crypto/bitcoin_prices.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Crypto', 'Price', 'Action', 'Status', 'Balance', 'Virtual Balance'])

def adjust_price(price, tick_size):
    return round(price / float(tick_size)) * float(tick_size)

def save_to_json(data):
    with open('/Users/jayananda/Documents/crypto/main.json', 'w') as file:
        json.dump(data, file)

start_time = datetime.datetime.now()

# Example Usage
check_symbol_validity("STORJUSDT")

crypto_list = [
    "storj",
]



crypto_data = {k: {
    "initial_price": v,
    "roof": v,
    "ground": v,
    "current_price": v,
    "lastsell_price": None,
    "status": "WAITING TO BUY",
    "symbol": symbols[k],
    "selling_price": None,
    "number_of_tokens": number_of_tokens[k],
    "balance": v * number_of_tokens[k],
    "virtual_balance": v * number_of_tokens[k],
    "tick_size": tick_size[k],

} for k, v in initial_prices.items()}

def fetch_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(crypto_list),
        "vs_currencies": "usd",
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch prices.")
        return None

def process_trading(crypto, current_price):
    last_price = crypto_data[crypto]["current_price"]
    crypto_data[crypto]["current_price"] = current_price
    initial_price = crypto_data[crypto]["initial_price"]
    lastsell_price = crypto_data[crypto]["lastsell_price"]
    status = crypto_data[crypto]["status"]
    nbtoken = crypto_data[crypto]["number_of_tokens"]
    crypto_data[crypto]["balance"] = nbtoken * initial_price
    crypto_data[crypto]["virtual_balance"] = nbtoken * current_price
    if current_price > crypto_data[crypto]["roof"] :
        crypto_data[crypto]["roof"] = current_price
    #idem for ground
    if current_price < crypto_data[crypto]["ground"]:
        crypto_data[crypto]["ground"] = current_price

    #percentage_from_initial = ((current_price - initial_price) / initial_price) * 100
    percentage_from_initial = ((current_price - initial_price) / initial_price) * 100
    #print(
    #    f"cur{current_price}init"
    #    f"{initial_price}s"
    #)
    percentage_change_from_last = ((current_price - last_price) / last_price) * 100 if last_price else 0
    percentage_change_from_roof = ((current_price - crypto_data[crypto]["roof"] ) / crypto_data[crypto]["roof"] ) * 100 if last_price else 0
    action = "HOLD"
    # Rule 1: Selling
    if status == "HOLD":
        action = "HOLD"
        if current_price > initial_price + initial_price * 0.01:
            crypto_data[crypto]["status"] = "GROWING WAIT TO SELL"
        elif current_price < initial_price - initial_price * 0.02:
            sell(crypto, current_price, "SOLD DOWN")
            action = "SELL"  # or "Buy" or "Sell" depending on the logic
            crypto_data[crypto]["status"] = "SOLD"

    elif status == "GROWING WAIT TO SELL":
        print(
            f"{percentage_change_from_roof }percentage_change_from_roof"
        )
        if abs(percentage_change_from_roof) > 1 and percentage_change_from_roof <= 0 :
            sell(crypto, current_price, "SOLD")
            print(
                f"ON SELL"
            )
            action = "SELL"  # or "Buy" or "Sell" depending on the logic
    elif status == "FORCE SELL":
        sell(crypto, current_price, "FORCE SELL")
        action = "SELL"  # or "Buy" or "Sell" depending on the logic
        crypto_data[crypto]["status"] = "FORCE SELL"


    # Rule 2: Buying
    elif status in ["SOLD", "SOLD DOWN", "WAITING TO BUY"]:
        if status == "SOLD":
            if current_price <= crypto_data[crypto]["ground"]:
                 crypto_data[crypto]["status"] = "WAITING TO BUY"  # Change status to wait for price to go up
                 action = "WAITING TO BUY"
        elif status == "WAITING TO BUY" and current_price > crypto_data[crypto]["ground"] * 1.005:
            buy(crypto, current_price)
            action = "BUY"
            crypto_data[crypto]["status"] = "HOLD"  # Reset the status after buying

    elapsed_time = datetime.datetime.now() - start_time
    hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    virtual_balance = crypto_data[crypto]['virtual_balance']
    balance = crypto_data[crypto]['number_of_tokens'] * crypto_data[crypto]['initial_price']
    crypto_name = crypto.capitalize()  # Assuming "crypto" variable contains the lowercase name
    write_to_csv([timestamp, crypto_name, current_price, action, status, balance, virtual_balance])

    print(
        f"{crypto.capitalize()}: €{current_price} (Status: {crypto_data[crypto]['status']},"
        f"{percentage_from_initial:+.2f}%,{percentage_change_from_last:+.2f}%, roof:{percentage_change_from_roof:+.2f}% ) ,{crypto_data[crypto]['balance']},{crypto_data[crypto]['virtual_balance']},{crypto_data[crypto]['roof']} {crypto_data[crypto]['roof']* 0.995} sell?  {int(hours)}h{int(minutes)}min{int(seconds)}s"
    )
    crypto_data[crypto]["current_price"] = current_price
    percentage_from_initial = ((current_price - initial_price) / initial_price) * 100
    # Compute the total initial investment
    total_initial_investment = sum([initial_prices[crypto] * number_of_tokens[crypto] for crypto in crypto_list])
    # print("Total Initial Investment: €{:.2f}".format(total_initial_investment))
    total_virtual_balance = sum([crypto_data[c]["virtual_balance"] for c in crypto_list])
    # print("Total Virtual Balance: €{:.2f}".format(total_virtual_balance))



def sell(crypto, current_price, status):
    crypto_data[crypto]["status"] = status
    crypto_data[crypto]["selling_price"] = current_price
    crypto_data[crypto]["lastsell_price"] = current_price
    # crypto_data[crypto]["number_of_tokens"] = 0
    print(f"{crypto.capitalize()} SELL at €{current_price} (Status: {status})")

    # Assuming you are selling all of your tokens for that specific crypto
    quantity = crypto_data[crypto]["number_of_tokens"]
    # Convert crypto name to a trading pair (e.g., "bitcoin" -> "BTCUSDT"). Modify if you use a different base currency
    #WAIT
    adjusted_price = adjust_price(current_price, crypto_data[crypto]["tick_size"])
    print(adjusted_price)  # this will print 0.231200
    api.sell(symbol=crypto_data[crypto]["symbol"], quantity=quantity,price=adjusted_price)

def buy(crypto, current_price):
    crypto_data[crypto]["status"] = "HOLD"
    crypto_data[crypto]["selling_price"] = None
    print(f"{crypto.capitalize()} BUY at €{current_price}")
    # For the sake of this example, I'm using a fixed quantity to buy.
    # You should adjust this based on your strategy or available funds.
    quantity = crypto_data[crypto]["number_of_tokens"]
    symbol = crypto.upper() + "EUR"

    #WAIT
    import pdb
    #pdb.set_trace()
    symbol_info = api.get_symbol_info("STORJUSDT")
    filters = symbol_info['symbols'][0]['filters']
    for filter in filters:
        if filter['filterType'] == 'PRICE_FILTER':
            print(filter)

    adjusted_price = adjust_price(current_price, crypto_data[crypto]["tick_size"])
    print(adjusted_price)  # this will print 0.231200
    response = api.buy(symbol=crypto_data[crypto]["symbol"], quantity=quantity,price=adjusted_price)
    print(response)
    transactions = api.view_transactions()
    print(transactions)

if __name__ == "__main__":

    while True:
        os.system('clear')
        prices = fetch_prices()
        total_initial_investment = sum([initial_prices[crypto] * number_of_tokens[crypto] for crypto in crypto_list])
        if prices:
            for crypto in crypto_list:
                current_price = prices.get(crypto, {}).get("usd")
                if current_price is not None:
                    process_trading(crypto, current_price)
        total_balance = sum([crypto_data[c]["balance"] for c in crypto_list])
        total_virtual_balance = sum([crypto_data[c]["virtual_balance"] for c in crypto_list])
        print(f"Total Balance: €{total_balance}, Total Virtual Balance: €{total_virtual_balance}")
        profit_or_loss = total_virtual_balance - total_initial_investment
        color = "green" if profit_or_loss >= 0 else "red"
        if supports_colors():
            print(colored("Profit/Loss: €{:.2f}".format(profit_or_loss), color))
        else:
            print("Profit/Loss: €{:.2f}".format(profit_or_loss))
        print(f"Initial Investment: €{total_initial_investment:.2f}")
        # Get balance every 10 seconds (or adjust the interval as needed)
        balances = api.get_balance()
        for asset, balance in balances.items():
            print(f"Asset: {asset}, Free: {balance['free']}, Locked: {balance['locked']}")

        save_to_json(crypto_data)  # Save the current state
        # Wait for 5 seconds before fetching and displaying prices again
        time.sleep(5)



