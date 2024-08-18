import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# for the following stock tickers, can you please share their clinical trials and related dates. 
# following this, we need to know each of their price 180 days prior to the clinical trial date.
    
# List of publicly traded companies involved in clinical trials
# companies = ["PFE", "JNJ", "MRK"]

# # Define the window size for the Simple Moving Average (SMA)
# window_size = 30

# # Calculate startDate and endDate
# end_date = datetime.today()
# start_date = end_date - timedelta(days=365 * 10)

# # Format dates in the format required by yfinance
# end_date_str = end_date.strftime('%Y-%m-%d')
# start_date_str = start_date.strftime('%Y-%m-%d')

# # Fetch historical data and calculate SMA
# for company in companies:
#     ticker = yf.Ticker(company)
    
#     # Get historical market data within the last 10 years
#     hist = ticker.history(start=start_date_str, end=end_date_str)
    
#     # Calculate the Simple Moving Average (SMA)
#     hist['SMA'] = hist['Close'].rolling(window=window_size).mean()
    
#     # Plot the closing prices and SMA
#     plt.figure(figsize=(12, 6))
#     plt.plot(hist['Close'], label=f'{company} Close Price')
#     plt.plot(hist['SMA'], label=f'{company} {window_size}-Day SMA', color='orange')
#     plt.title(f'{company} Stock Price and {window_size}-Day SMA')
#     plt.xlabel('Date')
#     plt.ylabel('Price (USD)')
#     plt.legend()
#     plt.show()

import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# Stock Tickers Clinical Trial Dates
tickers = {
    "JNJ": [
        {"startDate": "2020-09-01", "endDate": "2021-02-01"},
        {"startDate": "2013-03-01", "endDate": "2016-06-01"}
    ],
    "MRK": [
         {"startDate": "2020-10-01", "endDate": "2021-12-01"}
     ]
}

# Calculate stock prices 180 days before a given date
def get_price_180_before(ticker, date):
    date = datetime.strptime(date, "%Y-%m-%d")
    date_180_before = date - timedelta(days=180)
    stock_data = yf.download(ticker, start=date_180_before.strftime("%Y-%m-%d"), end=(date + timedelta(days=1)).strftime("%Y-%m-%d"))
    if not stock_data.empty:
        return stock_data.iloc[0]["Close"]
    else:
        return "No data"

# Calcualte stock price at a specific end date
def get_price_on_end_date(ticker, end_date):
    stock_data = yf.download(ticker, start=end_date, end=(datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"))
    if not stock_data.empty:
        return stock_data.iloc[0]["Close"]
    else:
        return "No data"

# Pull prices for each ticker
results = {}
for ticker, dates in tickers.items():
    results[ticker] = []
    for period in dates:
        start_price = get_price_180_before(ticker, period["startDate"])
        end_price = get_price_on_end_date(ticker, period["endDate"])
        results[ticker].append({
            "startDate": period["startDate"],
            "endDate": period["endDate"],
            "price_of_trial_180_before": start_price,
            "price_of_ticker_end": end_price
        })

# print(results)


stock_data = pd.read_csv('./data/Stock_Price_Data_for_Clinical_Trials.csv')
stock_data = stock_data[stock_data['End Price'] != 'No data']
stock_data['End Price'] = stock_data['End Price'].astype(float).round(2)
stock_data['Price 180 Days Before'] = stock_data['Price 180 Days Before'].astype(float).round(2)

analyze = pd.read_csv('./data/analyze.csv')
pd.set_option('display.max_columns', None)
print('analyze dataframe')
print(analyze)

print(analyze.info())
print(analyze.head())


import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.compat import lzip
import numpy as np

# Convert 'Phases' to a numeric format if it is categorical (e.g., Phase 1, Phase 2, etc.)
phase_mapping = {
    'Phase 1': 1,
    'Phase 2': 2,
    'Phase 3': 3,
    'Phase 4': 4
}

analyze['Phases'] = analyze['Phases'].map(phase_mapping)

# Stock Price Percentage Change
analyze['Price Change (%)'] = ((analyze['End Price'] - analyze['Price 180 Days Before']) / analyze['Price 180 Days Before']) * 100
print('Updated analyze dataframe with Price Change (%)')
print(analyze)

# Check for multicollinearity using Variance Inflation Factor (VIF)
X = analyze[['Phases', 'Enrollment Count']].fillna(0)
X = sm.add_constant(X)

vif = pd.DataFrame()
vif['VIF Factor'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
vif['features'] = X.columns
print("VIF values:")
print(vif)
X['Phases:Enrollment'] = X['Phases'] * X['Enrollment Count']

# Fit regression model with interaction terms
model = sm.OLS(analyze['Price Change (%)'], X).fit()
predictions = model.predict(X)
print(model.summary())

# Check for heteroskedasticity using Breusch-Pagan test
_, pval, __, f_pval = het_breuschpagan(model.resid, model.model.exog)
print(f'Breusch-Pagan test p-value: {pval}, F-test p-value: {f_pval}')

# Residuals plot for visual inspection of heteroskedasticity
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 6))
plt.scatter(predictions, model.resid)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Values')
plt.ylabel('Residuals')
plt.title('Residuals vs Predicted Values')
plt.show()

# Check for autocorrelation using Durbin-Watson test
from statsmodels.stats.stattools import durbin_watson
dw = durbin_watson(model.resid)
print(f'Durbin-Watson statistic: {dw}')

# Condensed Summary:
# --------------------------------------------------
# R-squared: 0.077 (The proportion of variance in the dependent variable that is predictable from the independent variables)
# Adjusted R-squared: -0.846 (Adjusted for the number of predictors in the model)
# F-statistic: 0.084 (The overall significance of the model)
# Prob (F-statistic): 0.821 (p-value for the F-statistic)

# Coefficient Estimates and Interpretation:
# Variable: Phases
#   Coefficient: 10.9088 (Interpretation: For a one-unit increase in Phases, the dependent variable changes by 10.9088, assuming all other variables are held constant)
#   Std Err: 12.0163 (The standard error of the coefficient estimate)
#   t-Statistic: 0.9078 (The ratio of the coefficient estimate to its standard error)
#   P>|t|: 0.5307 (p-value for the t-test on the coefficient)
# --------------------------------------------------

# Variable: Enrollment Count
#   Coefficient: -0.0000 (Interpretation: For a one-unit increase in Enrollment Count, the dependent variable changes by -0.0000, assuming all other variables are held constant)
#   Std Err: 0.0001 (The standard error of the coefficient estimate)
#   t-Statistic: -0.2891 (The ratio of the coefficient estimate to its standard error)
#   P>|t|: 0.8208 (p-value for the t-test on the coefficient)
# --------------------------------------------------

# Variable: Phases:Enrollment
#   Coefficient: -0.0001 (Interpretation: For a one-unit increase in Phases:Enrollment, the dependent variable changes by -0.0001, assuming all other variables are held constant)
#   Std Err: 0.0004 (The standard error of the coefficient estimate)
#   t-Statistic: -0.2891 (The ratio of the coefficient estimate to its standard error)
#   P>|t|: 0.8208 (p-value for the t-test on the coefficient)
# --------------------------------------------------

# Breusch-Pagan Test p-value: 0.2231 (Used to detect heteroskedasticity in the residuals)
# F-test p-value: 0.0049 (Alternative test for heteroskedasticity)

# Durbin-Watson statistic: 2.504 (Tests for autocorrelation in the residuals; values around 2 indicate no autocorrelation)


import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Stock Tickers Clinical Trial Dates
tickers = {
    "JNJ": [
        {"startDate": "2020-09-01", "trialDate": "2021-02-01"},
        {"startDate": "2013-03-01", "trialDate": "2016-06-01"}
    ],
    "MRK": [
         {"startDate": "2020-10-01", "trialDate": "2021-12-01"}
     ]
}

# Simple Moving Average (SMA) Window Size
window_size = 30

# Function to calculate and plot SMA
def plot_sma(ticker, start_date, end_date):
    # Fetch historical market data
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    # Calculate the Simple Moving Average (SMA)
    stock_data['SMA'] = stock_data['Close'].rolling(window=window_size).mean()
    
    # Plot the closing prices and SMA
    plt.figure(figsize=(12, 6))
    plt.plot(stock_data['Close'], label=f'{ticker} Close Price')
    plt.plot(stock_data['SMA'], label=f'{ticker} {window_size}-Day SMA', color='orange')
    plt.title(f'{ticker} Stock Price and {window_size}-Day SMA')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.show()

# Iterate through each ticker and date range to plot SMA
for ticker, periods in tickers.items():
    for period in periods:
        start_date = datetime.strptime(period["startDate"], "%Y-%m-%d").strftime('%Y-%m-%d')
        trial_date = datetime.strptime(period["trialDate"], "%Y-%m-%d")
        end_date = (trial_date + timedelta(days=60)).strftime('%Y-%m-%d')  # trial_date plus 2 months
        plot_sma(ticker, start_date, end_date)
