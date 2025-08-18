# main.py
import os
import time
from dotenv import load_dotenv
from scanner import create_exchanges, get_tradable_pairs, scan_arbitrage
from config import CHECK_INTERVAL

load_dotenv()

if __name__ == "__main__":
    print("🚀 Запуск Crypto Arbitrage Scanner — 24/7")
    print("💡 Бот ищет разницу цен. Торгуй вручную по сигналам!\n")

    exchanges = create_exchanges()
    if not exchanges:
        print("❌ Не удалось подключиться ни к одной бирже.")
        exit()

    top_symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'TRX', 'ADA', 'DOT', 'LINK', 'MATIC', 'AVAX', 'LTC' 'HYPE' 'XLM' 'SUI' 'BCH' 'HBAR' 'AVAX' 'TON' 'UNI' 'APT' 'ICP' 'PI' 'POL' 'ARB' 'SEI' 'CHZ' 'CFX' 'IOTA' 'BEAM' 'ZRO' 'MOVE' 'BERA']
    print(f"🔍 Используем топ-монет: {', '.join(top_symbols)}")

    pairs = get_tradable_pairs(exchanges, top_symbols)
    if not pairs:
        print("❌ Не найдено общих торговых пар.")
        exit()

    print(f"✅ Начинаю сканирование {len(pairs)} пар каждые {CHECK_INTERVAL} сек...")
    print("-------------------------------\n")

    while True:
        try:
            scan_arbitrage(exchanges, pairs)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n🛑 Остановлено пользователем.")
            break
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            time.sleep(10)
