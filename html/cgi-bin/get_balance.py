#!/bin/env python3
#fileencoding:utf-8
print("Content-Type:text/html\n")
#print open('../info/balance').read()

#!/bin/env python
#fileencoding:utf-8
import sqlite3
# test.db is a file in the working directory.
conn = sqlite3.connect("../balance.db")


#where = 'where 1=1'
# create tables

c = conn.execute(''' select ts, json_data from total_balance where id = (select max(id) from total_balance) ''')

ret = []
for item in c:
    ret.append((item[0], item[1]))

conn.close()

(ts, json_data) = ret[0]
import datetime
ts = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
import sys
sys.path.append('..')
import json
import trading
import logger
log = logger.get_logger('get_balance')
trading.log = log

if ts >= datetime.datetime.now() - datetime.timedelta(minutes=1):
    log.info('the latest date in data.db is new, just use it.')
    print(json_data)
else:
    log.info('the latest date in data.db is old, directly get the balance.')
    spot = trading.okcoinSpot
    future = trading.okcoinFuture
    trading.get_information(spot, future)
    
    import json
    print(json.dumps(trading.get_balance(spot, future)))
