import sqlite3

# test.db is a file in the working directory.
conn = sqlite3.connect("data.db")

c = conn.cursor()

import traceback
# create tables
#c.execute(''' Drop table tickers''')


try:
    c.execute('''CREATE TABLE tickers
      (id integer primary key autoincrement, local_time datetime, market_time datetime, name text, buy decimal(10, 5), sell decimal(10,5)) ''')
except Exception as e:
    print(traceback.format_exc())

try:
    c.execute('''create index local_time_index on tickers (local_time)''')
except Exception as e:
    print(traceback.format_exc())
conn.commit()
conn.close()

conn = sqlite3.connect('balance.db')
c = conn.cursor()
try:
    c.execute(''' CREATE TABLE total_balance (id integer primary key autoincrement, ts datetime, balance decimal(10, 5), json_data varchar(300)) ''')
except Exception as e:
    print(traceback.format_exc())

try:
    c.execute('''create index ts_index on total_balance (ts)''')
except Exception as e:
    print(traceback.format_exc())

# save the changes
conn.commit()

# close the connection with the database
conn.close()
