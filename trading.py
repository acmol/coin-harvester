#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果


import time
from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture
import sys

#初始化apikey，secretkey,url

import logger

log = logger.get_logger('trading')

from conf import OPEN_RATES, CLOSE_RATES, ADJUST_VALUES, apikey, secretkey, SUPPORT_COIN_TYPES, WORKING_CONTRACT_TYPE


okcoinRESTURL = 'www.okex.com'   #请求注意：国内账号需要 修改为 www.okcoin.cn

#现货API
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

#期货API
okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)


import datetime

MARKETS = {}

def try_it(n, sleep_time=2):
    def _w(fn):
        def _f(*args, **kargs):
            m = n
            while True:
                m -= 1
                try:
                    return fn(*args, **kargs)
                except Exception as e:
                    import traceback
                    log.info(str(e) + '\n' + traceback.format_exc())
                    log.info('Error with args: %s, kargs: %s'% (str(args), str(kargs)))
                    time.sleep(sleep_time)
                    if m <= 0:
                        raise
            
        return _f
    return _w


class UnexpectedFreedCoinException(RuntimeError):
    def __init__(self, type_msg, freezed_cnt):
        self.freezed_cnt = freezed_cnt
        return super(Exception, self).__init__('[%s] There are some unexpected freezed coins. freezed_cnt = %s' % (type_msg, freezed_cnt))

contract_price = {'btc': 100}
default_price = 10

def get_contract_price(coin):
    return contract_price.get(coin, default_price)


def make_order(market_infos, need, coin, total_coin, total_usdt):
    import copy
    market_infos = copy.deepcopy(market_infos)
    no_need_future = False
    no_need_spot = False
    for market, market_info in market_infos.items():
        if market == 'spot':
            depth = market_info['depth']
            market_infos[market] = {}
            market_infos[market]['adjust_asks'] = [ {'price': price, 'ad_price': market_info['adjust'] * price, 'coin_amount': amount} for (price, amount) in depth['asks']]
            market_infos[market]['adjust_bids'] = [ {'price': price, 'ad_price': market_info['adjust'] * price, 'coin_amount': amount} for (price, amount) in depth['bids']]
        else:
            depth = market_info['depth']
            market_infos[market] = {}
            market_infos[market]['adjust_asks'] = [ {'price': price, 'ad_price': market_info['adjust'] * price, 'amount': amount, 'coin_amount': amount * get_contract_price(coin) / price} for (price, amount) in depth['asks']]
            market_infos[market]['adjust_bids'] = [ {'price': price, 'ad_price': market_info['adjust'] * price, 'amount': amount, 'coin_amount': amount * get_contract_price(coin) / price} for (price, amount) in depth['bids']]

    if need > 0:
        asks = []
        for market, market_info in market_infos.items():
            for ask in market_info['adjust_asks']:
                asks.append((market, ask))
        asks.sort(key = lambda v: v[1]['ad_price'])

        orders = []
        need_buy = need
        usdt_total = total_usdt
        log.info('need_buy is [%s], usdt_total is [%s]' %(need_buy, usdt_total))
        sys.stdout.flush()

        for (market, ask) in asks:
            if no_need_spot and no_need_future:
                return orders
            if market == 'spot':
                if no_need_spot:
                    continue
                coin_amount = ask['coin_amount']
                coin_can_buy = usdt_total / ask['price']
                if coin_can_buy <= 0.001:
                    no_need_spot = True
                    continue
                buy_amount = min(need_buy, coin_can_buy, coin_amount)

                if buy_amount <= 0.001:
                    continue
                if buy_amount > 0:
                    orders.append({'market': market, 'symbol': coin + "_usdt", 'amount': buy_amount, 'price': ask['price'], 'type': 'buy'})

                need_buy -= buy_amount
                usdt_total -= buy_amount * buy_amount
                if need_buy <= 0.001:
                    print ('need amount is about 0, exit')
                    sys.stdout.flush()
                    return orders
            else:
                if no_need_future:
                    continue
                coin_amount = ask['coin_amount']
                if coin_amount < need_buy:
                    buy_amount = ask['amount']
                    need_buy -= coin_amount
                    orders.append({'market': market, 'symbol': coin + '_usdt', 'amount': buy_amount, 'price': ask['price'], 'type': 'buy', 'contract_type': market})
                else:
                    amount = need_buy * ask['price'] /  get_contract_price(coin)
                    print ('buy amount is %s, floor it to %s' %(amount, int(amount)))
                    sys.stdout.flush()
                    buy_amount = int(amount)
                    if buy_amount != 0:
                        orders.append({'market': market, 'symbol': coin + '_usdt', 'amount': buy_amount, 'price': ask['price'], 'type': 'buy', 'contract_type': market})
                    print ('need amount too small, exit')
                    sys.stdout.flush()
                    no_need_fture = True
        return orders
    elif need < 0:
        bids = []
        for market, market_info in market_infos.items():
            for bid in market_info['adjust_bids']:
                bids.append((market, bid))
        bids.sort(key = lambda v: -1 * v[1]['ad_price'])

        orders = []
        need_sell = -need
        coin_total = total_coin
        print ('need_sell is [%s], coin_total is [%s]' %(need_sell, coin_total))
        sys.stdout.flush()
        for mbid in bids:
            if no_need_spot and no_need_future:
                return orders
            (market, bid) = mbid
            if market == 'spot':
                if no_need_spot:
                    continue
                if coin_total <= 0.001:
                    no_need_spot = True
                    continue
                
                coin_amount = bid['coin_amount']
                sell_amount = min(need_sell, coin_total, coin_amount)

                orders.append({'market': market, 'symbol': coin + "_usdt", 'amount': sell_amount, 'price': bid['price'], 'type': 'sell'})
                need_sell -= sell_amount
                coin_total -= sell_amount

                #FIXME: magic number
                if need_sell <= 0.001:
                    print ('need amount too small, exit.')
                    sys.stdout.flush()
                    print (orders)
                    sys.stdout.flush()
                    no_need_spot = True
                    
            else:
                if no_need_future:
                    continue
                coin_amount = bid['coin_amount']
                if coin_amount < need_sell:
                    sell_amount = bid['amount']
                    need_sell -= coin_amount
                    orders.append({'market': market, 'symbol': coin + '_usdt', 'amount': sell_amount, 'price': bid['price'], 'type': 'sell', 'contract_type': market})
                else:
                    amount = need_sell * bid['price'] /  get_contract_price(coin)
                    print ('sell amount is %s, floor it to %s' %(amount, int(amount)))
                    sys.stdout.flush()
                    sell_amount = int(amount)
                    if sell_amount != 0:
                        orders.append({'market': market, 'symbol': coin + '_usdt', 'amount': sell_amount, 'price': bid['price'], 'type': 'sell', 'contract_type': market})
                    print ('need amount too small, exit')
                    sys.stdout.flush()
                    no_need_future=True

        log.warning('this is not normal, because all market orders will be eatten')
        return orders


def debug_info(fn):
    def _fn(*p, **k):
        log.debug('before [%s] the MARKETS is %s' %(str(fn), str(MARKETS)))
        ret = fn(*p, **k)
        log.debug('after [%s] the MARKETS is %s' %(str(fn), str(MARKETS)))
        return ret
    return _fn

@debug_info
def suggestion(coin_market, future_market, coin, contract_type):
    symbol = coin + '_usdt'
    coin_depth = try_it(3)(coin_market.depth)(symbol)
    future_depth = try_it(3)(future_market.future_depth)(symbol, contract_type, 20)
    #coin_position = try_it(3)(coin_market.position)()
    #future_position = try_it(3)(future_market.future_position)()
    coin_userinfo = MARKETS['spot']['userinfo']
    future_userinfo = MARKETS['future']['userinfo']
    future_position = try_it(3)(future_market.future_position_4fix)(symbol, contract_type)

    #print (type(future_userinfo), future_userinfo)
    sys.stdout.flush()
    future_coin_info = future_userinfo['info'][coin]
    #availables = [contract['available'] for contract in future_coin_info['contracts'] if contract['contract_type'] == contract_type]
    #assert len(availables) <= 1, str(list(available))
    #available = 0
    #if len(availables) == 1:
    #    available = availables[0]

    # print (coin_userinfo)
    sys.stdout.flush()

    if coin_userinfo['info']['funds']['freezed'][coin] != 0:
        type_msg = symbol
        raise UnexpectedFreedCoinException(type_msg, coin_userinfo['info']['funds']['freezed'][coin])

    if coin_userinfo['info']['funds']['freezed']['usdt'] != 0:
        type_msg = 'usdt'
        raise UnexpectedFreedCoinException(type_msg, coin_userinfo['info']['funds']['freezed']['usdt'])

    holding = future_position['holding']
    holding = list(filter(lambda hold: hold['contract_type'] == contract_type, holding))
    assert len(holding) <= 1, str(list(holding))
    log.debug('holding is %s' % str(holding))
    free_coin = coin_userinfo['info']['funds']['free'][coin]
    rights = future_coin_info['rights']
    if len(holding) == 0:
        need = - free_coin - rights
        log.debug('holding empty, MARKETS= %s' % str(MARKETS))
        log.debug('free_coin = %f, rights = %f' % (free_coin, rights))
    else:
        holding = holding[0]
        holding_coin_amount = holding['sell_amount'] * 1.0 * get_contract_price(coin) / MARKETS['future']['ticker']['last']
        need =  holding_coin_amount - free_coin -  rights
        log.debug('holding = %s' % str(holding))
        log.info('holding_coin_amount = %f' % holding_coin_amount)
        log.info('free_coin = %f' % free_coin)
        log.info('rights = %f' % rights)

    log.info("need coin " + str(need) + " (" + str(coin) + ")")
    if -0.01< need < 0.01:
        return []

    market_info={}
    market_info['spot'] = {'depth': coin_depth, 'adjust': ADJUST_VALUES[coin] }
    market_info[contract_type] = {'depth': future_depth, 'adjust': 1.0 }

    total_coin = future_coin_info['balance'] + free_coin
    total_usdt = coin_userinfo['info']['funds']['free']['usdt']
    MARKETS['total_usdt'] = total_usdt
    return make_order(market_info, need, coin, total_coin=total_coin, total_usdt=total_usdt)



@try_it(3)
def devolve_for_sell(coin_market, future_market, coin_type, coin_amount):
    log.info('devolve for sell ' + str(coin_amount) + str(coin_type))
    to_devolve = coin_amount - MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type]
    if to_devolve < 0:
        return None 
    future_market.future_devolve(coin_type + '_usdt', '2', to_devolve)
    MARKETS['spot']['userinfo'] = try_it(3)(coin_market.userinfo)()
    MARKETS['future']['userinfo'] = try_it(3)(future_market.future_userinfo_4fix)()
    to_devolve = coin_amount - MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type]
    assert -0.01 <= to_devolve <= 0.01, str((coin_amount, MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type], to_devolve))
    return MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type]

@try_it(3)
def devolve_all_to_future(coin_market, future_market, coin_type):
    log.info('devole all to future ' + str(coin_type))
    to_devolve = MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type]
    future_market.future_devolve(coin_type + '_usdt', '1', to_devolve)
    MARKETS['spot']['userinfo'] = try_it(3)(coin_market.userinfo)()
    MARKETS['future']['userinfo'] = try_it(3)(future_market.future_userinfo_4fix)()
    assert MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type] < 0.01, str(MARKETS)
    return MARKETS['spot']['userinfo']['info']['funds']['free'][coin_type]

def get_infomation(coin_market, future_market, symbol=None, contract_type=None):
    MARKETS['spot'] = {}
    MARKETS['future'] = {}
    MARKETS['spot']['userinfo'] = try_it(3)(coin_market.userinfo)()
    MARKETS['future']['userinfo'] = try_it(3)(future_market.future_userinfo_4fix)()
    if symbol and contract_type:
        MARKETS['future']['ticker'] = try_it(3)(future_market.future_ticker)(symbol, contract_type)['ticker']

def run_after_split(to_split, n, fn):
    sys.stdout.flush()
    pos = 0
    while pos < len(to_split):
        fn(to_split[pos: pos + n])
        pos += n


MAX_ORDER_IN_ONE_REQUEST = 5
def send_spot_orders(spot_market, orders):
    def _send_spot_orders(s_orders):
        assert len(s_orders) > 0
        symbol = s_orders[0]['symbol']
        log.info('symbol = %s, s_orders = %s' %(symbol, s_orders))
        log.info(str(spot_market.batchTrade(symbol, s_orders)))
    if orders:
        log.warning('send_spot_orders' + str(orders))
    run_after_split(orders, MAX_ORDER_IN_ONE_REQUEST, _send_spot_orders)

def send_future_orders(future_market, orders):
    def _send_future_orders(s_orders):
        assert len(s_orders) > 0
        symbol = s_orders[0]['symbol']
        contract_type = s_orders[0]['contract_type']
        s_orders = list(map(lambda order: order.update({'type': '4' if order['type'] == 'buy' else '2'}) or order, s_orders))
        log.info(str(future_market.future_batchTrade(symbol, contract_type, s_orders, leverRate=10)))
        sys.stdout.flush()
    if orders:
        log.warning('send_future_orders' + str(orders))
    run_after_split(orders, MAX_ORDER_IN_ONE_REQUEST, _send_future_orders)

#初始化程序
def cancel_trade(symbol):
    sumOrders = 0
    marketFailed = False
    #先取消现货订单
    spotTradeDict = okcoinSpot.orderinfo(symbol, -1)
    spotReturn = spotTradeDict['result']
    #print(spotTradeDict)
    sys.stdout.flush()
    if spotReturn:      #如果获取现货订单成功
        log.debug("get spot trade successed")
        sys.stdout.flush()
        listOrdersId = []
        listOrders = spotTradeDict['orders']
        lengthOrders = len(listOrders)
        sumOrders = sumOrders + lengthOrders

        log.debug("spot orders : " + str(lengthOrders))
        sys.stdout.flush()

        #获取需要取消的orderID
        for index in range(0, lengthOrders):
            statusValue = listOrders[index]['status']
            if statusValue == 0 or statusValue == 1:
                listOrdersId.append(listOrders[index]['order_id'])
        #开始取消现货市场的交易
        orderIdLen = len(listOrdersId)
        for index in range(0, orderIdLen):
            okcoinSpot.cancelOrder(symbol, listOrdersId[index])
    else:
        #return False
        marketFailed = True
        log.info("get spot trade failed")

    #再取消期货订单
    futuresList = ["this_week", "next_week", "quarter"]
    lenFuturesList = len(futuresList)
    for index in range(0, lenFuturesList):
        futureTradeDict = okcoinFuture.future_orderinfo(symbol, futuresList[index], -1, 1, 1, 50)   #确认page的意思
        futureReturn = futureTradeDict['result']
        if futureReturn:
            log.debug("get future trade succeed")
            listOrdersId =[]
            listOrders = futureTradeDict['orders']
            lenOrders = len(listOrders)

            log.debug(futuresList[index] + " future orders : " + str(lenOrders))
            sys.stdout.flush()

            sumOrders = sumOrders + lenOrders
            #获取需要取消的orderID
            for item in range(0, lenOrders):
                statusValue = listOrders[item]['status']
                if statusValue == 0 or statusValue == 1:
                    listOrdersId.append(listOrders[item]['order_id'])
            #开始取消期货市场的交易
            futureOrderIdLen = len(listOrdersId)
            for item in range(0, futureOrderIdLen):
                okcoinFuture.future_cancel(symbol, futuresList[index], listOrdersId[item])

        else:
            #return False
            marketFailed = True
            log.info("get future trade failed")
    #如果市场订单信息总数为0，则代表当前没有订单。不为0代表当前还有订单
    return sumOrders == 0 and not marketFailed
    # if sumOrders == 0 and not marketFailed:
    #     return True
    # else:
    #     return False

@try_it(3)
def init_trade(symbol):
    tryCount = 0
    cancelStatus = False
    while True:
        log.info("init_trade : " + str(tryCount))
        sys.stdout.flush()
        cancelStatus = cancel_trade(symbol)
        tryCount = tryCount + 1
        if cancelStatus:
            break
        assert tryCount <= 5, 'try to cancel order fail after tried 5 times'
    return cancelStatus

def get_user_contract_balance(future_market, coin_type, contract_type):
    coin_balance = MARKETS['future']['userinfo']['info'][coin_type]
    contract = [contract for contract in coin_balance['contracts'] if contract['contract_type'] == contract_type]
    assert len(contract) == 1
    contract = contract[0]
    return contract

def get_profit(future_market, coin_type, contract_type):
    contract = get_user_contract_balance(future_market, coin_type, contract_type)
    return contract['profit'] + contract['unprofit']

# 计算期货市场最少需要做空多少张合约
# 因为赢利部分是不能提现的，故而必须做空相应价值的合约
# 另，暂时没做自动取出保证金的功能，所以如果保证金过多，也需要做空对应的合约。
def future_get_min_sell_amount(future_market, coin_type, contract_type, current_price):
    profit = get_profit(future_market, coin_type, contract_type)
    if profit < 0:
        return 0
    else:
        contract = get_user_contract_balance(future_market, coin_type, contract_type)
        log.debug(contract)
        bond = contract['bond']

        return int(max(bond, profit) * current_price / get_contract_price(coin_type))


def get_balance(spot_market, future_market):
    total_balance = 0
    balance_info = {'info': { }}
    for coin in SUPPORT_COIN_TYPES:
        coin_depth = try_it(3)(spot_market.depth)(coin + '_usdt')
        balance_info['info'][coin] = {}
        balance_info['info'][coin]['price'] = coin_depth['bids'][0][0]
        balance_info['info'][coin]['amount'] =  MARKETS['spot']['userinfo']['info']['funds']['freezed'][coin] + MARKETS['spot']['userinfo']['info']['funds']['free'][coin] + MARKETS['future']['userinfo']['info'][coin]['rights']
        log.info('%s %s %s' % (coin, coin_depth['bids'][0][0], balance_info['info'][coin]['amount']))
        total_balance += coin_depth['bids'][0][0] * (MARKETS['spot']['userinfo']['info']['funds']['freezed'][coin] + MARKETS['spot']['userinfo']['info']['funds']['free'][coin] + MARKETS['future']['userinfo']['info'][coin]['rights'])

    total_usdt = MARKETS['spot']['userinfo']['info']['funds']['free']['usdt']
    balance_info['info']['usdt'] = {'amount': total_usdt, 'price': 1}
    balance_info['total'] = total_balance + total_usdt

    log.info('usdt %s' % total_usdt)
    log.info('total_balance = ' + str(total_balance + total_usdt))
    log.info ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    return balance_info


def future_get_max_sell_amount(future_market, coin_type, contract_type, current_price):
    holding = try_it(3)(future_market.future_position_4fix)(coin_type + '_usdt', contract_type)
    holding = holding['holding']
    holding = [hold for hold in holding if hold['contract_type'] == contract_type]
    if len(holding) == 0:
        return 0
    sell_amount = holding[0]['sell_amount']
    min_sell_amount = future_get_min_sell_amount(future_market, coin_type, contract_type, current_price)
    log.info('min_sell_amount= ' + str(min_sell_amount))
    return sell_amount - min_sell_amount

def get_contract_amount_by_coin_amount(coin_amount, contract_price, coin_type):
    return int(coin_amount * contract_price / get_contract_price(coin_type))

def get_coin_amount_by_contract_amount(contract_amount, contract_price, coin_type):
    return contract_amount * get_contract_price(coin_type) / contract_price

def judge(coin_type, contract_type):
    symbol = coin_type + '_usdt'
    spot_depth = try_it(3)(okcoinSpot.depth)(symbol)
    future_depth = try_it(3)(okcoinFuture.future_depth)(symbol, contract_type, 20)

    total_usdt = MARKETS['spot']['userinfo']['info']['funds']['free']['usdt']
    spot_sell_1 = spot_depth['asks'][-1]
    spot_buy_1 = spot_depth['bids'][0]

    future_sell_1 = future_depth['asks'][-1]
    future_buy_1 = future_depth['bids'][0]

    if future_sell_1[0] < spot_buy_1[0] * CLOSE_RATES[coin_type]:
        future_sell_1_amount = future_sell_1[1]
        future_max_sell_amount = future_get_max_sell_amount(okcoinFuture, coin_type, contract_type, future_sell_1[0])
        spot_buy_1_equality_amount = get_contract_amount_by_coin_amount(spot_buy_1[1], future_sell_1[0], coin_type)

        log.info('future_sell_1_amount = %d, future_max_sell_amount = %d, spot_buy_1_equality_amount = %d' %(future_sell_1_amount, future_max_sell_amount, spot_buy_1_equality_amount))

        amount = min(future_sell_1_amount, future_max_sell_amount, spot_buy_1_equality_amount)

        if amount > 0:
            log.warning('[Close][%s#%s] Should buy future and sell spot, future_sell_1[0] / spot_buy_1[0] = %s'%(coin_type, contract_type, future_sell_1[0] / spot_buy_1[0]))
            send_future_orders(okcoinFuture, [{'symbol': symbol, 'amount': amount, 'price': future_sell_1[0], 'type': 'buy', 'contract_type': contract_type}])

    if future_buy_1[0] > spot_sell_1[0] * OPEN_RATES[coin_type]:
        
        spot_max_can_buy_amount = int(1000 * total_usdt / spot_sell_1[0])/1000.0
        spot_sell_1_amount = spot_sell_1[1]
        future_buy_1_equality_amount = get_coin_amount_by_contract_amount(future_buy_1[1], future_buy_1[0], coin_type)
        
        log.info('spot_max_can_buy_amount = %f' % spot_max_can_buy_amount)
        log.info('spot_sell_1_amount = %f' % spot_sell_1_amount)
        log.info('future_buy_1_equality_amount = %f' % future_buy_1_equality_amount)

        amount = min(spot_max_can_buy_amount, spot_sell_1_amount, future_buy_1_equality_amount)

        min_amount = max(0.001, (get_contract_price(coin_type) / future_buy_1[0]))

        if amount >= min_amount:
            log.warning('[Open][%s#%s] Should sell future and buy spot, future_buy_1[0] / spot_sell_1[0] = '% (coin_type, contract_type) + str(future_buy_1[0] / spot_sell_1[0]))
            send_spot_orders(okcoinSpot, [{'symbol': symbol, 'amount': amount, 'price': spot_sell_1[0], 'type': 'buy'}])

    log.info('%s#%s future_sell_1[0] / spot_buy_1[0] = %s' % (coin_type, contract_type, future_sell_1[0] / spot_buy_1[0]))
    log.info('%s#%s future_buy_1[0] / spot_sell_1[0] = %s' % (coin_type, contract_type, future_buy_1[0] / spot_sell_1[0]))

def run_orders(spot_market, future_market, orders, coin_type):
    spot_orders = [order for order in orders if order['market'] == 'spot']
    future_orders = [order for order in orders if order['market'] != 'spot']
    
    total_spot_amount = sum(map(lambda order: order['amount'], spot_orders))
    log.info('total spot amout :' + str(total_spot_amount))
    if len(spot_orders) != 0 and spot_orders[0]['type'] == 'sell':
        devolve_for_sell(spot_market, future_market, coin_type, total_spot_amount)
    send_spot_orders(spot_market, spot_orders)
    devolve_all_to_future(spot_market, future_market, coin_type)
    send_future_orders(future_market, future_orders)



def main():
    while True:
        for coin_type in SUPPORT_COIN_TYPES:
            contract_type=WORKING_CONTRACT_TYPE
            local_time = datetime.datetime.now()
            msg = '##########################\n' + str(local_time) + ':current coin type is [' + coin_type + ']'
            log.info(msg)
            symbol = coin_type + '_usdt'
            init_trade(symbol)

            get_infomation(okcoinSpot, okcoinFuture, symbol, contract_type)
            judge(coin_type, contract_type)

            init_trade(symbol)
            get_infomation(okcoinSpot, okcoinFuture, symbol, contract_type)

            local_time = datetime.datetime.now()

            orders = suggestion(okcoinSpot, okcoinFuture, coin_type, contract_type)
            times = 0
            while len(orders) != 0:
                try:
                    run_orders(okcoinSpot, okcoinFuture, orders, coin_type)
                except Exception as e:
                    log.info('exception occurred')
                    import traceback
                    log.info(traceback.format_exc())
                init_trade(symbol)
                get_infomation(okcoinSpot, okcoinFuture, symbol, contract_type)
                orders = suggestion(okcoinSpot, okcoinFuture, coin_type, contract_type)
                assert times <= 3, 'tried to balance, but failed 3 times' + str(orders)
                times += 1

            total_balance = 0
            balance_info = {'info': { }}
            log.info ('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
            for coin in SUPPORT_COIN_TYPES:
                coin_depth = try_it(3)(okcoinSpot.depth)(coin + '_usdt')
                balance_info['info'][coin] = {}
                balance_info['info'][coin]['price'] = coin_depth['bids'][0][0]
                balance_info['info'][coin]['amount'] =  MARKETS['spot']['userinfo']['info']['funds']['freezed'][coin] + MARKETS['spot']['userinfo']['info']['funds']['free'][coin] + MARKETS['future']['userinfo']['info'][coin]['rights']
                log.info('%s %s %s' % (coin, coin_depth['bids'][0][0], balance_info['info'][coin]['amount']))

                total_balance += coin_depth['bids'][0][0] * (MARKETS['spot']['userinfo']['info']['funds']['freezed'][coin] + MARKETS['spot']['userinfo']['info']['funds']['free'][coin] + MARKETS['future']['userinfo']['info'][coin]['rights'])

            total_usdt = MARKETS['spot']['userinfo']['info']['funds']['free']['usdt']
            balance_info['info']['usdt'] = {'amount': total_usdt, 'price': 1}
            balance_info['total'] = total_balance + total_usdt

            import json
            with open('info/.balance-writting', 'w') as bf:
                json.dump(balance_info, bf)
            import os
            os.rename('info/.balance-writting', 'info/balance')
            log.info('usdt %s' % total_usdt)
            log.info('total_balance = ' + str(total_balance + total_usdt))
            log.info ('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            init_trade(symbol)

if __name__ == "__main__":
    n = 0
    while True:
        try:
            main()
        except Exception as e:
            n += 1
            log.exception(e)
            log.warning("exception occurred, retry... it's the %d time(s)" % n)

# get_infomation(okcoinSpot, okcoinFuture)
# print (future_get_max_sell_amount(okcoinFuture, 'etc', 'next_week', 289))

# # print (MARKETS['future']['userinfo'], '\n============================')
# sys.stdout.flush()
# # future_position = try_it(3)(okcoinFuture.future_position_4fix)('etc_usdt', 'next_week')

# # print (future_position)
# sys.stdout.flush()

# etc 273.9652 48.50407788
# etc 29.1803 9.03788610661
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# total_balance = 13554.589049844257
