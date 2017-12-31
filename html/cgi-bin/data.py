#!/bin/env python
#fileencoding:utf-8
import sqlite3
print("Content-Type:text/html\n")
# test.db is a file in the working directory.
conn = sqlite3.connect("../data.db")

import cgi

# 创建 FieldStorage 的实例化
form = cgi.FieldStorage()

# 获取数据
n = form.getvalue('n')
c = form.getvalue('c').split('-')
t = form.getvalue('t').split('-')

where = ' where name in (' + ','.join(["'" + i + '_usdt' + "', '" + i + '_usdt#' + j + "'" for i in c for j in t]) + ')'

#where = 'where 1=1'
# create tables

cols = ['id', 'local_time', 'name', 'buy', 'sell']
c = conn.execute(''' select * from (select %s from tickers %s order by id desc limit %s) order by id''' % (','.join(cols), where, n))

ret = []
for item in c:
    ret.append(dict(zip(cols, item)))

import json
print(json.dumps(ret))
# close the connection with the database
conn.close()

