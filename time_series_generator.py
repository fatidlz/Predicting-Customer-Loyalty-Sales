import pandas as pd
import sqlite3

conn = sqlite3.connect("crm_demo.db")
sql = """
SELECT 
  date(t.transaction_date) AS day,
  SUM(t.total_amount_eur) AS total_sales<
FROM Transactions t
JOIN Products p ON t.product_id = p.product_id
WHERE p.product_type = 'Capsule'
GROUP BY day
ORDER BY day;
"""
df = pd.read_sql_query(sql, conn)

# Datetime ,index
df['day'] = pd.to_datetime(df['day'])
df.set_index('day', inplace=True)

# from 0
df = df.asfreq('D', fill_value=0)

# save as CSV
df.to_csv("daily_capsule_sales.csv")
print("CSV file created: daily_capsule_sales.csv")

print(df.head())
