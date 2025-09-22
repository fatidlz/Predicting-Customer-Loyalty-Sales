#-------------------------------------------Regression---------------------------------------

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# -------------------------------
# 1. Load Data
# -------------------------------
df = pd.read_csv("daily_capsule_sales.csv", parse_dates=['day'], index_col='day')
df['total_sales'] = df['total_sales'].fillna(0)

# -------------------------------
# 2. Create 7-day lag features
# -------------------------------
lags = 7
for i in range(1, lags+1):
    df[f'lag_{i}'] = df['total_sales'].shift(i)

# Drop rows with NaN (first 7 rows)
df = df.dropna()

# Features (previous 7 days)
X = df[[f'lag_{i}' for i in range(1, lags+1)]].values
# Target (today's sales)
y = df['total_sales'].values

# -------------------------------
# 3. Split into Train/Test (70/30)
# -------------------------------
split_idx = int(len(df) * 0.7)
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]
dates_train = df.index[:split_idx]
dates_test = df.index[split_idx:]

# -------------------------------
# 4. Train Linear Regression
# -------------------------------
model = LinearRegression()
model.fit(X_train, y_train)

# -------------------------------
# 5. Prediction and Evaluation
# -------------------------------
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print("Test RMSE:", rmse)

# -------------------------------
# 6. Plot Results
# -------------------------------
plt.figure(figsize=(14,6))
plt.plot(dates_train, y_train, label='Train (Actual)', color='blue')
plt.plot(dates_test, y_test, label='Test (Actual)', color='green')
plt.plot(dates_test, y_pred, label='Forecast (7-day Regression)', color='red', linestyle='--')

plt.title('Daily Capsule Sales - 7-Day Lag Linear Regression Forecast')
plt.xlabel('Date')
plt.ylabel('Total Sales (EUR)')
plt.legend()
plt.grid(True)

# Save the forecast chart as image
plt.savefig("capsule_sales_7day_regression_forecast.png", dpi=150)
print("Forecast chart saved as capsule_sales_7day_regression_forecast.png")

plt.show()

"""

##-------------------------------------------ARIMA---------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error

# -------------------------------
# 1. Load Data
# -------------------------------
df = pd.read_csv("daily_capsule_sales.csv", parse_dates=['day'], index_col='day')
df['total_sales'] = df['total_sales'].fillna(0)

# -------------------------------
# 2. Split into Train/Test
# -------------------------------
split_idx = int(len(df) * 0.7)
train = df.iloc[:split_idx]['total_sales']
test = df.iloc[split_idx:]['total_sales']

# -------------------------------
# 3. Auto ARIMA Model
# -------------------------------
model = auto_arima(train,
                   start_p=1, start_q=1,
                   max_p=7, max_q=7,
                   d=None,           # Let auto_arima decide differencing
                   seasonal=False,   # no seasonality for now
                   trace=True,       # show tested models
                   error_action='ignore',
                   suppress_warnings=True,
                   stepwise=True)

print(model.summary())

# -------------------------------
# 4. Forecast
# -------------------------------
n_test = len(test)
forecast = model.predict(n_periods=n_test)

# RMSE
rmse = np.sqrt(mean_squared_error(test, forecast))
print("Test RMSE:", rmse)

# -------------------------------
# 5. Plot Results
# -------------------------------
plt.figure(figsize=(14,6))
plt.plot(train.index, train, label='Train (Actual)', color='blue')
plt.plot(test.index, test, label='Test (Actual)', color='green')
plt.plot(test.index, forecast, label='Forecast (Auto ARIMA)', color='red', linestyle='--')

plt.title('Daily Capsule Sales - Auto ARIMA Forecast')
plt.xlabel('Date')
plt.ylabel('Total Sales (EUR)')
plt.legend()
plt.grid(True)

# Save chart
plt.savefig("capsule_sales_auto_arima_forecast.png", dpi=150)
print("Forecast chart saved as capsule_sales_auto_arima_forecast.png")

plt.show()
"""
