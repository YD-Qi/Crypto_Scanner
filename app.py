from flask import Flask, escape, request, render_template
from patterns import candlestick_patterns
from all_coin_symbols import *
import ccxt
import pandas as pd
import time
import talib as ta
import os
exchange = ccxt.binance()

app = Flask(__name__)

@app.route('/snapshot')
def snapshot():
    for coin in all_coin_symbols:
        df = pd.DataFrame(exchange.fetch_ohlcv(coin, timeframe='8h', limit=500))
        df.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Vol']
        df['Datetime'] = df['Datetime'].apply(
            lambda x: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(x / 1000.)))
        symbol = coin.partition('/')[0]
        df.to_csv('datasets/individual_coins/{}.csv'.format(symbol))
    return{
        'code': 'success'
    }

@app.route('/')
def index():
    pattern  = request.args.get('pattern', False)
    stocks = {}

    for coin in all_coin_symbols:
        coin = coin.partition('/')[0]
        stocks[coin] = {'coin_symbol': coin}

    if pattern:
        for coin in all_coin_symbols:
            coin = coin.partition('/')[0]
            df = pd.read_csv('datasets/individual_coins/{}.csv'.format(coin))
            pattern_function = getattr(ta, pattern)

            try:
                results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = results.tail(1).values[0]

                if last > 0:
                    stocks[coin][pattern] = 'bullish'
                elif last < 0:
                    stocks[coin][pattern] = 'bearish'
                else:
                    stocks[coin][pattern] = None
            except Exception as e:
                print(e)

    return render_template('index.html', candlestick_patterns=candlestick_patterns, stocks=stocks, pattern=pattern)
