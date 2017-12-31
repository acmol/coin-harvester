import sqlite3

# test.db is a file in the working directory.
conn = sqlite3.connect("data.db")

c = conn.cursor()


# create tables
#c.execute(''' Drop table tickers''')
c.execute('''CREATE TABLE tickers
      (id integer primary key autoincrement, local_time datetime, market_time datetime, name text, buy decimal(10, 5), sell decimal(10,5)) ''')

# save the changes
conn.commit()

# close the connection with the database
conn.close()