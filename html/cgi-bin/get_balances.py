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
import cgi

# 创建 FieldStorage 的实例化
form = cgi.FieldStorage()

# 获取数据
n = form.getvalue('n')
c = conn.execute(''' select json_data from (select id, ts, json_data from total_balance order by id desc limit ?) order by id''', (n,))

import json
balances = []
for (json_data,) in c:
    balances.append(json.loads(json_data))

conn.close()

import sys
sys.path.append('..')

import conf

inital_usdt = conf.__dict__.get('INITAL_USDT', 0)

result = {
        'inital_usdt': inital_usdt,
        'balances': balances
        }

print (json.dumps(result))
