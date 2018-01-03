import trading
import logger
import conf
import os
import datetime
log = logger.get_logger('monitor')
trading.log = log

def get_information():
    trading.get_information(trading.okcoinSpot, trading.okcoinFuture)
    return trading.MARKETS

def get_balance():
    return trading.get_balance(trading.okcoinSpot, trading.okcoinFuture)


def is_trading_running():
    p = os.popen("ps ux | grep $PWD/trading.py | grep -v grep")
    trading_program = p.read()
    p.close()
    return len(trading_program) != 0

def stop_trading(exit=False):
    import sys
    os.system("sh stop.sh")
    p = os.popen("ps ux")
    ps_info = p.read()
    p.close()
    log.warn('[STOPED] after running stop.sh, let\'s see if it\'s still there: ' + ps_info)
    if exit:
        sys.exit(-1)


def is_balance_ok(balance, markets):
    if conf.WARNING_IF_BALANCE_LESS_THAN >= balance['total']:
        log.warn('[STOPED]total balance is [%f], it\'s leass than the configure value [%f], so the program will be stoped' %(balance['total'], conf.WARNING_IF_BALANCE_LESS_THAN))
        log.warn('[STOPED]total balance is [%f], it\'s leass than the configure value [%f], so the program will be stoped' %(balance['total'], conf.WARNING_IF_BALANCE_LESS_THAN))
        log.warn('[STOPED]total balance is [%f], it\'s leass than the configure value [%f], so the program will be stoped' %(balance['total'], conf.WARNING_IF_BALANCE_LESS_THAN))
        return False
    return True


class BalanceSaver(object):
    def __init__(self):
        import sqlite3
        self.connection = sqlite3.connect("balance.db")

    def save_balance(self, balance):
        import json
        local_time = datetime.datetime.now()
        lt = local_time.strftime('%Y-%m-%d %H:%M:%S')
        c = self.connection.cursor()
        c.execute(''' insert into total_balance (ts, balance, json_data) values(?, ?, ?) ''' , (lt, balance['total'], json.dumps(balance)))
        self.connection.commit()



import time
if __name__ == "__main__":
    markets = get_information()
    balance = get_balance()
    if conf.WARNING_IF_BALANCE_LESS_THAN * 1.2 < balance['total']:
        log.warning('Your setting of WARNING_IF_BALANCE_LESS_THAN is too small!')

    saver = BalanceSaver()
    
    error_cnt = 0
    while True:
        try:
            if not is_trading_running():
                log.warn('trading is not runing, is there something wrong??')
                time.sleep(3 * 60)
                continue
            
            markets = get_information()
            balance = get_balance()
            if not is_balance_ok(balance, markets):
                stop_trading()
            saver.save_balance(balance)

            error_cnt = 0
        except Exception as e:
            import traceback
            log.info(traceback.format_exc())
            error_cnt +=1
            if error_cnt >=5:
                log.warn('[STOPED]monitor failed 5 times, so stop trading')
                stop_trading()
            time.sleep(3)
                
        time.sleep(10)


    
