import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Load Data
# ---------------------------
ticker = "AAPL"
data = yf.download(ticker, start="2015-01-01", end="2023-12-31", auto_adjust=True)
data = data[['Close']]

# ---------------------------
# Calculate Moving Averages
# ---------------------------
data['SMA50'] = data['Close'].rolling(window=50).mean()
data['SMA200'] = data['Close'].rolling(window=200).mean()
data.dropna(inplace=True)

# ---------------------------
# Generate Signals
# ---------------------------
data['Signal'] = 0
data.loc[data['SMA50'] > data['SMA200'], 'Signal'] = 1
data.loc[data['SMA50'] < data['SMA200'], 'Signal'] = -1
data['Position'] = data['Signal'].diff().fillna(0)

# ---------------------------
# Backtest
# ---------------------------
initial_cash = 10000
cash = initial_cash
position = 0.0
portfolio_values = []

for idx, row in data.iterrows():
    price = float(row['Close'])  # Ensure scalar
    signal = float(row['Position'])  # Ensure scalar

    # Buy
    if signal == 1.0 and cash > 0:
        position = cash / price
        cash = 0.0

    # Sell
    elif signal == -1.0 and position > 0:
        cash = position * price
        position = 0.0

    portfolio_value = cash + position * price
    portfolio_values.append(portfolio_value)

data['Portfolio'] = portfolio_values

# ---------------------------
# Plot Results
# ---------------------------
plt.figure(figsize=(14, 6))
plt.plot(data.index, data['Close'], label='AAPL Price', alpha=0.6)
plt.plot(data.index, data['SMA50'], label='SMA50', alpha=0.75)
plt.plot(data.index, data['SMA200'], label='SMA200', alpha=0.75)
plt.plot(data.index, data['Portfolio'], label='Portfolio Value', color='green', linestyle='--')
plt.title('SMA Crossover Strategy on AAPL')
plt.xlabel('Date')
plt.ylabel('Price / Portfolio Value')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ---------------------------
# Print Final Result
# ---------------------------
final_value = float(data['Portfolio'].iloc[-1])
total_return = (final_value - initial_cash) / initial_cash * 100
print(f"Final Portfolio Value: ${final_value:,.2f}")
print(f"Total Return: {total_return:.2f}%")

data.to_csv("data.csv")