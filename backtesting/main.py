from tracemalloc import start
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class Backtester:
    def __init__(self, symbol, start_date, end_date, initial_capital=100000):
        """
        Initialize the Backtester with stock data 

        Parameters:
        symbol: Stock symbol (e.g. 'TCS.NS', 'AAPL', 'SBI.NS') - Yahoo Finance for symbol details
        start_date: Start Date for Backtesting (YYYY-MM-DD)
        end_date: End Date for Backtesting (YYYY-MM-DD)
        initial_capital: Starting Capital for Trading
        """
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.historical_data = None

    def get_data(self):
        """
        Fetch data from Yahoo Finance
        """
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(start=self.start_date, end=self.end_date)
            print(f"Data Fetched for {self.symbol}: {len(self.data)} days")
            return True
        except Exception as e:
            print(f"Error fetching the data: {e}")
            return False
        
    def moving_average_strategy(self, short_window=20, long_window=50):
        """
        Implement a simple moving average crossover strategy

        Parameters:
        short_window: Period for short-term moving average
        long_window: Period for long-term moving average
        """
        if self.data is None:
            print("No data available. Please get teh data for desired period")
            return

        #Calculate MA        
        self.data['SMA_short'] = self.data['Close'].rolling(window=short_window).mean()
        self.data['SMA_long'] = self.data['Close'].rolling(window=long_window).mean()

        # Generate Signals
        self.data['Signal'] = 0
        self.data['Signal'][short_window:] = np.where(self.data['SMA_short'][short_window:] > self.data['SMA_long'][short_window:], 1, 0)

        # self.data.to_csv("/home/nish/Code/py-lab/backtesting/data.csv")

        
        

if __name__ == "__main__":

    today_date = datetime.now().strftime('%Y-%m-%d')
    bt_ex = Backtester('TCS.NS', '2000-01-01', today_date, 10000)
    bt_ex.get_data()
    bt_ex.moving_average_strategy()