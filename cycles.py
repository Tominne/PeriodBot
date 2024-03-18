import sqlite3
from sqlite3 import Error




def create_connection():
    conn = None
    try:
      conn = sqlite3.connect('periodTracker.db')
      print(f'connected with tracker')
    except Error as e:
      print(e)
    return conn

def sql_query(query, params=None):
  

  conn = create_connection()
  if conn is not None:
    try:
      c = conn.cursor()
      if params:
        c.execute(query, params)
      else:
        c.execute(query)
      conn.commit()
      print('data inserted')
    except Error as e:
      print(e)

def get_startDate(query, user_id):
  conn = create_connection()
  if conn is not None:
    try:
      c = conn.cursor()
      c.execute('SELECT start_date FROM periods WHERE user_id = ?', (user_id,))
      row = c.fetchone()
      if row is not None:
        last_start_date = row[0]
      else:
        last_start_date = None 
      return last_start_date
    except Error as e:
      print(e)
  
create_period_table_query = """
CREATE TABLE IF NOT EXISTS periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_date TEXT NOT NULL
)
"""

conn = create_connection()
if conn is not None:
  sql_query(create_period_table_query)
else:
  print("Error cant connect to sql db")
