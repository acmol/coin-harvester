#!/bin/env python3
#fileencoding:utf-8
print("Content-Type:text/html\n")
#print open('../info/balance').read()

import sys
sys.path.append('..')
import trading
spot = trading.okcoinSpot
import logger
log = logger.get_logger('get_balance')
trading.log = log
future = trading.okcoinFuture
trading.get_information(spot, future)

import json
print (json.dumps(trading.get_balance(spot, future)))
