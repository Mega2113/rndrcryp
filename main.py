import ccxt
import pandas as pd
import ta
import time
from datetime import datetime
from telegram.ext import Updater
import requests

# টেলিগ্রাম বট ফাংশন
def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# Fibonacci Levels ক্যালকুলেট করার ফাংশন
def calculate_fibonacci_levels(high, low):
    diff = high - low
    levels = {
        "23.6%": high - (diff * 0.236),
        "38.2%": high - (diff * 0.382),
        "50%": high - (diff * 0.5),
        "61.8%": high - (diff * 0.618),
        "78.6%": high - (diff * 0.786)
    }
    return levels

# সিগন্যাল জেনারেট করার ফাংশন
def generate_signal(symbol, timeframe='4h'):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # RSI ক্যালকুলেট
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    
    # MACD ক্যালকুলেট
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    
    # Fibonacci Levels
    recent_high = df['high'].iloc[-50:].max()
    recent_low = df['low'].iloc[-50:].min()
    fib_levels = calculate_fibonacci_levels(recent_high, recent_low)
    
    # বাই সিগন্যাল লজিক
    current_price = df['close'].iloc[-1]
    current_rsi = df['rsi'].iloc[-1]
    macd_line = df['macd'].iloc[-1]
    signal_line = df['macd_signal'].iloc[-1]
    
    buy_signal = False
    if current_rsi < 30 and macd_line > signal_line:
        buy_signal = True
    
    return {
        "symbol": symbol,
        "price": current_price,
        "rsi": current_rsi,
        "macd": macd_line,
        "signal_line": signal_line,
        "fib_levels": fib_levels,
        "buy_signal": buy_signal
    }

def main():
    # টেলিগ্রাম টোকেন এবং চ্যাট আইডি
    TELEGRAM_TOKEN = "8183606037:AAFjy17QzwVpc9u0faVhmmbkyKgVP5UpaaQ"  # BotFather থেকে টোকেন
    CHAT_ID = "7026116515"  # তোমার টেলিগ্রাম চ্যাট আইডি (BotFather থেকে পাওয়া যায়)
    
    # ক্রিপ্টোকারেন্সি লিস্ট
    coins = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]  # আরো কয়েন যোগ করতে পারো
    
    while True:
        message = f"🔍 ক্রিপ্টো সিগন্যাল ({datetime.now()})\n\n"
        for coin in coins:
            signal = generate_signal(coin, timeframe='4h')
            if signal['buy_signal']:
                fib_text = "\n".join([f"{key}: {value:.2f}" for key, value in signal['fib_levels'].items()])
                message += (
                    f"🪙 {coin}\n"
                    f"💰 Price: {signal['price']:.2f}\n"
                    f"📊 RSI: {signal['rsi']:.2f}\n"
                    f"📈 MACD: {signal['macd']:.2f}\n"
                    f"🔍 Signal Line: {signal['signal_line']:.2f}\n"
                    f"📏 Fibonacci Levels:\n{fib_text}\n"
                    f"✅ Buy Signal: YES\n\n"
                )
            else:
                message += f"🪙 {coin}: No Buy Signal\n\n"
        
        # টেলিগ্রামে মেসেজ পাঠানো
        send_telegram_message(TELEGRAM_TOKEN, CHAT_ID, message)
        
        # ২ ঘণ্টা (7200 সেকেন্ড) অপেক্ষা
        time.sleep(7200)

if __name__ == '__main__':
    main()
