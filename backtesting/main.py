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
        

if __name__ == "__main__":

    today_date = datetime.now().strftime('%Y-%m-%d')
    bt_ex = Backtester('TCS.NS', '2000-01-01', today_date, 10000)
    bt_ex.get_data()