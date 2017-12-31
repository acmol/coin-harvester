#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果


import time
from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture
from HttpMD5Util import buildMySign,httpGet,httpPost

#初始化apikey，secretkey,url

apikey='3aa75f67-37a6-4b84-b4a2-659b8833a9e8'
secretkey='89068E9364E4BC4F0574B9BDDAE2E4C5'

okcoinRESTURL = 'www.okex.com'   #请求注意：国内账号需要 修改为 www.okcoin.cn

#现货API
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

#期货API
okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)

import sqlite3

# test.db is a file in the working directory.
conn = sqlite3.connect("data.db")

c = conn.cursor()

import datetime


def try_it(n):
    def _w(fn):
        def _f(*args, **kargs):
            m = n
            while m > 0:
                m -= 1
                try:
                    return fn(*args, **kargs)
                except Exception as e:
                    print (e)
                    print ('Error with args: %s, kargs: %s'% (str(args), str(kargs)))
                    time.sleep(2)
            return None
        return _f
    return _w

def save_ticker(name, ticker, local_time):
    l = local_time.strftime('%Y-%m-%d %H:%M:%S')
    t = datetime.datetime.fromtimestamp(int(ticker['date'])).strftime('%Y-%m-%d %H:%M:%S')
    n = name
    tk = ticker['ticker']
    b = tk['buy']
    s = tk['sell']
    c.execute('''
        insert into tickers (local_time, market_time, name, buy, sell) values('%s', '%s', '%s', %s, %s)
    ''' %(l, t, n, b, s))

@try_it(3)
def get_and_save_ticker(name, markets, local_time, which_future=None):
    ticker = None

    if which_future is None:
        show_name = name
        ticker = markets.ticker(name)
    else:
        show_name = name + '#' + which_future
        ticker = markets.ticker(name, which_future)

    print(ticker)

    save_ticker(show_name, ticker, local_time)
    return ticker

while True:
    local_time = datetime.datetime.now()
    ltc = get_and_save_ticker('btc_usdt', okcoinSpot, local_time)
    time.sleep(1)
    get_and_save_ticker('btc_usdt', okcoinFuture, local_time, 'this_week')
    time.sleep(1)
    ltc_next = get_and_save_ticker('btc_usdt', okcoinFuture, local_time, 'next_week')
    time.sleep(1)
    get_and_save_ticker('btc_usdt', okcoinFuture, local_time, 'quarter')   
    
    etc = get_and_save_ticker('etc_usdt', okcoinSpot, local_time)
    time.sleep(1)
    get_and_save_ticker('etc_usdt', okcoinFuture, local_time, 'this_week')
    time.sleep(1)
    etc_next = get_and_save_ticker('etc_usdt', okcoinFuture, local_time, 'next_week')
    time.sleep(1)
    get_and_save_ticker('etc_usdt', okcoinFuture, local_time, 'quarter')
 
    get_and_save_ticker('ltc_usdt', okcoinSpot, local_time)
    time.sleep(1)
    get_and_save_ticker('ltc_usdt', okcoinFuture, local_time, 'this_week')
    time.sleep(1)
    get_and_save_ticker('ltc_usdt', okcoinFuture, local_time, 'next_week')
    time.sleep(1)
    get_and_save_ticker('ltc_usdt', okcoinFuture, local_time, 'quarter')

    get_and_save_ticker('bch_usdt', okcoinSpot, local_time)
    time.sleep(1)
    get_and_save_ticker('bch_usdt', okcoinFuture, local_time, 'this_week')
    time.sleep(1)
    get_and_save_ticker('bch_usdt', okcoinFuture, local_time, 'next_week')
    time.sleep(1)
    get_and_save_ticker('bch_usdt', okcoinFuture, local_time, 'quarter')
    
    get_and_save_ticker('eth_usdt', okcoinSpot, local_time)
    time.sleep(1)
    get_and_save_ticker('eth_usdt', okcoinFuture, local_time, 'this_week')
    time.sleep(1)
    get_and_save_ticker('eth_usdt', okcoinFuture, local_time, 'next_week')
    time.sleep(1)
    get_and_save_ticker('eth_usdt', okcoinFuture, local_time, 'quarter')
    conn.commit()

    time.sleep(10)

#print (u' 现货历史交易信息 ')
#print (okcoinSpot.trades())

#print (u' 用户现货账户信息 ')
#print (okcoinSpot.userinfo())

#print (u' 现货下单 ')
#print (okcoinSpot.trade('ltc_usd','buy','0.1','0.2'))

#print (u' 现货批量下单 ')
#print (okcoinSpot.batchTrade('ltc_usd','buy','[{price:0.1,amount:0.2},{price:0.1,amount:0.2}]'))

#print (u' 现货取消订单 ')
#print (okcoinSpot.cancelOrder('ltc_usd','18243073'))

#print (u' 现货订单信息查询 ')
#print (okcoinSpot.orderinfo('ltc_usd','18243644'))

#print (u' 现货批量订单信息查询 ')
#print (okcoinSpot.ordersinfo('ltc_usd','18243800,18243801,18243644','0'))

#print (u' 现货历史订单信息查询 ')
#print (okcoinSpot.orderHistory('ltc_usd','0','1','2'))

#print (u' 期货行情信息')
#print (okcoinFuture.future_ticker('ltc_usd','this_week'))

#print (u' 期货市场深度信息')
#print (okcoinFuture.future_depth('btc_usd','this_week','6'))

#print (u'期货交易记录信息')
#print (okcoinFuture.future_trades('ltc_usd','this_week'))

#print (u'期货指数信息')
#print (okcoinFuture.future_index('ltc_usd'))

#print (u'美元人民币汇率')
#print (okcoinFuture.exchange_rate())

#print (u'获取预估交割价')
#print (okcoinFuture.future_estimated_price('ltc_usd'))

#print (u'获取全仓账户信息')
#print (okcoinFuture.future_userinfo())

#print (u'获取全仓持仓信息')
#print (okcoinFuture.future_position('ltc_usd','this_week'))

#print (u'期货下单')
#print (okcoinFuture.future_trade('ltc_usd','this_week','0.1','1','1','0','20'))

#print (u'期货批量下单')
#print (okcoinFuture.future_batchTrade('ltc_usd','this_week','[{price:0.1,amount:1,type:1,match_price:0},{price:0.1,amount:3,type:1,match_price:0}]','20'))

#print (u'期货取消订单')
#print (okcoinFuture.future_cancel('ltc_usd','this_week','47231499'))

#print (u'期货获取订单信息')
#print (okcoinFuture.future_orderinfo('ltc_usd','this_week','47231812','0','1','2'))

#print (u'期货逐仓账户信息')
#print (okcoinFuture.future_userinfo_4fix())

#print (u'期货逐仓持仓信息')
#print (okcoinFuture.future_position_4fix('ltc_usd','this_week',1))




