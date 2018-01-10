#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果


import time
from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture
from HttpMD5Util import buildMySign,httpGet,httpPost
import logger

log = logger.get_logger('data_saver')
#初始化apikey，secretkey,url

from conf import apikey, secretkey

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
                    log.info (e)
                    log.info ('Error with args: %s, kargs: %s'% (str(args), str(kargs)))
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

    log.info(ticker)

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

    time.sleep(30)

