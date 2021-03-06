import time
from binance import Client
from binance.enums import ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, SIDE_BUY, SIDE_SELL, TIME_IN_FORCE_GTC
import pandas as pd

from exchanger import getBianceClient


client = getBianceClient()
qty = 10
rio = 1


def getMinuteData(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(
        symbol, interval, lookback))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    return frame


def strategy(symbol, qty=qty, entried=False, rio = 1):
    df = getMinuteData(symbol, '1h', '10 hour ago UTC')
    compond = (df.Open.astype(float).pct_change() +
               1).astype(float).cumprod() - 1
    print(compond[-1])
    if not entried:
        if compond[-1] < -0.03:
            order = Client.create_order(
                self=client, symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=qty)
            targetPrice = format(float(order['fills'][0]['price']) * 1.02, '.8f')
            print(targetPrice)
            rio = (rio * float(targetPrice)/float(order['fills'][0]['price'])) -0.001
            Client.create_order(self=client, symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_LIMIT, quantity=qty,   timeInForce=TIME_IN_FORCE_GTC, price=targetPrice)
            entried = True
            print(rio)
        else:
            print('No trade has been executed')
            time.sleep(900)
            strategy('XRPBTC', qty, entried=False, rio = rio)
    if entried:
        while True:
            print(rio)
            time.sleep(900)
            orders = client.get_open_orders(symbol='XRPBTC')
            print(rio)
            if len(orders) < 3:
                entried = False
                strategy('XRPBTC', qty, entried=False)


orders = client.get_open_orders(symbol='XRPBTC')
if len(orders) < 3:
    hasOrders = False
else:
    hasOrders = True
strategy('XRPBTC', qty, entried=hasOrders, rio = 1)
