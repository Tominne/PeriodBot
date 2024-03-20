import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
from cycles import sql_query, get_startDate
from discord.ext import commands

def create_connection():
    conn = None
    try:
      conn = sqlite3.connect('periodTracker.db')
      print(f'connected with tracker')
    except Error as e:
      print(e)
    return conn

def predict_next_start_date(user_id):
  conn = create_connection()
  if conn is None:
    try:
      c = conn.cursor()
      c.execute('SELECT start_date, duration FROM periods WHERE user_id = ? ORDER BY start_date', (user_id))
      rows = c.fetchall()
      if rows is not None and len(rows) > 1:
        diffs = [(datetime.strptime(rows[i+1][0], '%Y-%m-%d %H:%M:%S:%f') - datetime.strftime(rows[i][0], '%Y-%m-%d %H:%M:%S:%f')).days for i in range(len(rows)-1)]
        durations = [row[1] for row in rows if row[1] is not None]
        avg_diff = sum(diffs) / len(diffs)
        avg_duration = sum(durations) / len(durations) if durations else None
        next_start_date = datetime.strftime(rows[-1][0], '%Y-%m-%d %H:%M:%S:%f') + timedelta(days=avg_diff)
        return next_start_date, avg_duration
    except Error as e:
      print(e)



  