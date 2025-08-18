# scanner.py
import ccxt
from config import EXCHANGES, QUOTE_SYMBOL, SPREAD_THRESHOLD
from notify import log_signal, send_telegram

def create_exchanges():
    exchange_map = {}
    for name in EXCHANGES:
        try:
            ex = getattr(ccxt, name)({
                'apiKey': os.getenv(f'{name.upper()}_API_KEY'),
                'secret': os.getenv(f'{name.upper()}_SECRET'),
                'enableRateLimit': True,
            })
            ex.load_markets()
            exchange_map[name] = ex
            log_signal(f"✅ Подключено: {name.capitalize()}")
        except Exception as e:
            log_signal(f"❌ Ошибка подключения к {name}: {e}")
    return exchange_map

def get_tradable_pairs(exchanges, symbols):
    common_pairs = set()
    all_markets = {}

    for ex_name, ex in exchanges.items():
        markets = ex.markets
        exchange_pairs = set()
        for symbol in symbols:
            pair = f"{symbol}/{QUOTE_SYMBOL}"
            if pair in markets and markets[pair]['active']:
                exchange_pairs.add(pair)
        all_markets[ex_name] = exchange_pairs

    for pair in set.union(*all_markets.values()):
        count = sum(1 for pairs in all_markets.values() if pair in pairs)
        if count >= 2:
            common_pairs.add(pair)

    pairs_list = list(common_pairs)
    log_signal(f"🔍 Найдено {len(pairs_list)} общих торгуемых пар")
    return pairs_list

def scan_arbitrage(exchanges, pairs):
    for symbol in pairs:
        prices = {}
        for name, ex in exchanges.items():
            try:
                ticker = ex.fetch_ticker(symbol)
                price = ticker['last']
                if price > 0:
                    prices[name] = price
            except Exception as e:
                pass

        if len(prices) < 2:
            continue

        min_price = min(prices.values())
        max_price = max(prices.values())
        min_exchange = [k for k, v in prices.items() if v == min_price][0]
        max_exchange = [k for k, v in prices.items() if v == max_price][0]
        spread = ((max_price - min_price) / min_price) * 100

        if spread >= SPREAD_THRESHOLD:
            base = symbol.split('/')[0]
            message = (
                f"🔥 АРБИТРАЖ [{base}]\n"
                f"🟢 Покупай: {min_exchange.capitalize()} → {min_price:.4f}\n"
                f"🔴 Продавай: {max_exchange.capitalize()} → {max_price:.4f}\n"
                f"📈 Спред: {spread:.2f}%"
            )
            log_signal(message)
            if __import__('config').ENABLE_TELEGRAM:
                send_telegram(message)
