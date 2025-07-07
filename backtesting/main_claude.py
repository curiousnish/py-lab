import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class Backtester:
    def __init__(self, symbol, start_date, end_date, initial_capital=10000):
        """
        Initialize the backtester with stock data
        
        Parameters:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        start_date: Start date for backtesting (YYYY-MM-DD)
        end_date: End date for backtesting (YYYY-MM-DD)
        initial_capital: Starting capital for trading
        """
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.data = None
        self.signals = None
        self.portfolio = None
        
    def fetch_data(self):
        """Fetch historical data using yfinance"""
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(start=self.start_date, end=self.end_date)
            print(f"Data fetched for {self.symbol}: {len(self.data)} days")
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False
    
    def moving_average_strategy(self, short_window=20, long_window=50):
        """
        Implement a simple moving average crossover strategy
        
        Parameters:
        short_window: Period for short-term moving average
        long_window: Period for long-term moving average
        """
        if self.data is None:
            print("No data available. Please fetch data first.")
            return
        
        # Calculate moving averages
        self.data['SMA_short'] = self.data['Close'].rolling(window=short_window).mean()
        self.data['SMA_long'] = self.data['Close'].rolling(window=long_window).mean()
        
        # Generate signals
        self.data['Signal'] = 0
        self.data['Signal'][short_window:] = np.where(
            self.data['SMA_short'][short_window:] > self.data['SMA_long'][short_window:], 1, 0
        )
        
        # Generate trading positions (1 for buy, 0 for sell)
        self.data['Position'] = self.data['Signal'].diff()
        
        print(f"Strategy signals generated: {short_window}-day SMA vs {long_window}-day SMA")
    
    def calculate_returns(self):
        """Calculate portfolio returns and performance metrics"""
        if self.data is None or 'Signal' not in self.data.columns:
            print("No signals available. Please run a strategy first.")
            return
        
        # Calculate daily returns
        self.data['Returns'] = self.data['Close'].pct_change()
        
        # Calculate strategy returns (only when we have a position)
        self.data['Strategy_Returns'] = self.data['Returns'] * self.data['Signal'].shift(1)
        
        # Calculate cumulative returns
        self.data['Cumulative_Returns'] = (1 + self.data['Returns']).cumprod()
        self.data['Cumulative_Strategy_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        
        # Calculate portfolio value
        self.data['Portfolio_Value'] = self.initial_capital * self.data['Cumulative_Strategy_Returns']
        
        print("Returns calculated successfully")
    
    def get_performance_metrics(self):
        """Calculate and display performance metrics"""
        if self.data is None:
            return
        
        # Remove NaN values for calculations
        strategy_returns = self.data['Strategy_Returns'].dropna()
        market_returns = self.data['Returns'].dropna()
        
        # Calculate metrics
        total_return = (self.data['Portfolio_Value'].iloc[-1] - self.initial_capital) / self.initial_capital
        market_return = (self.data['Cumulative_Returns'].iloc[-1] - 1)
        
        # Annualized returns (assuming 252 trading days per year)
        days = len(strategy_returns)
        annualized_return = (1 + total_return) ** (252 / days) - 1
        annualized_market_return = (1 + market_return) ** (252 / days) - 1
        
        # Volatility (annualized)
        strategy_volatility = strategy_returns.std() * np.sqrt(252)
        market_volatility = market_returns.std() * np.sqrt(252)
        
        # Sharpe ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / strategy_volatility if strategy_volatility != 0 else 0
        
        # Maximum drawdown
        cumulative = self.data['Cumulative_Strategy_Returns'].fillna(1)
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        winning_trades = strategy_returns[strategy_returns > 0]
        win_rate = len(winning_trades) / len(strategy_returns[strategy_returns != 0]) if len(strategy_returns[strategy_returns != 0]) > 0 else 0
        
        metrics = {
            'Total Return': f"{total_return:.2%}",
            'Market Return': f"{market_return:.2%}",
            'Annualized Return': f"{annualized_return:.2%}",
            'Annualized Market Return': f"{annualized_market_return:.2%}",
            'Volatility': f"{strategy_volatility:.2%}",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}",
            'Maximum Drawdown': f"{max_drawdown:.2%}",
            'Win Rate': f"{win_rate:.2%}",
            'Total Trades': len(strategy_returns[strategy_returns != 0]),
            'Final Portfolio Value': f"${self.data['Portfolio_Value'].iloc[-1]:,.2f}"
        }
        
        return metrics
    
    def plot_results(self):
        """Plot the backtesting results"""
        if self.data is None:
            return
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # Plot 1: Price and Moving Averages
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', linewidth=1)
        if 'SMA_short' in self.data.columns:
            ax1.plot(self.data.index, self.data['SMA_short'], label='Short MA', alpha=0.7)
            ax1.plot(self.data.index, self.data['SMA_long'], label='Long MA', alpha=0.7)
        
        # Mark buy/sell signals
        if 'Position' in self.data.columns:
            buy_signals = self.data[self.data['Position'] == 1]
            sell_signals = self.data[self.data['Position'] == -1]
            
            ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', 
                       marker='^', s=100, label='Buy Signal')
            ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', 
                       marker='v', s=100, label='Sell Signal')
        
        ax1.set_title(f'{self.symbol} - Price and Signals')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Portfolio Value vs Buy & Hold
        if 'Portfolio_Value' in self.data.columns:
            ax2.plot(self.data.index, self.data['Portfolio_Value'], 
                    label='Strategy Portfolio', linewidth=2)
            
            # Buy & Hold comparison
            buy_hold_value = self.initial_capital * self.data['Cumulative_Returns']
            ax2.plot(self.data.index, buy_hold_value, 
                    label='Buy & Hold', linewidth=2, alpha=0.7)
            
            ax2.set_title('Portfolio Value Comparison')
            ax2.set_ylabel('Portfolio Value ($)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # Plot 3: Drawdown
        if 'Cumulative_Strategy_Returns' in self.data.columns:
            cumulative = self.data['Cumulative_Strategy_Returns'].fillna(1)
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            
            ax3.fill_between(self.data.index, drawdown, alpha=0.3, color='red')
            ax3.plot(self.data.index, drawdown, color='red', linewidth=1)
            ax3.set_title('Strategy Drawdown')
            ax3.set_ylabel('Drawdown (%)')
            ax3.set_xlabel('Date')
            ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Example usage and demonstration
def run_example_backtest():
    """Run a complete example backtest"""
    print("=== Trading Strategy Backtesting Demo ===\n")
    
    # Initialize backtester
    bt = Backtester(
        symbol='AAPL',
        start_date='2020-01-01',
        end_date='2024-01-01',
        initial_capital=10000
    )
    
    # Fetch data
    print("1. Fetching data...")
    if not bt.fetch_data():
        return
    
    # Run strategy
    print("\n2. Running moving average strategy...")
    bt.moving_average_strategy(short_window=20, long_window=50)
    
    # Calculate returns
    print("\n3. Calculating returns...")
    bt.calculate_returns()
    
    # Get performance metrics
    print("\n4. Performance Metrics:")
    metrics = bt.get_performance_metrics()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Plot results
    print("\n5. Plotting results...")
    bt.plot_results()
    
    return bt

# Run the example
if __name__ == "__main__":
    # You'll need to install required packages:
    # pip install pandas numpy matplotlib yfinance
    
    backtester = run_example_backtest()
    
    # You can also create your own backtest like this:
    # my_bt = Backtester('MSFT', '2021-01-01', '2023-01-01', 5000)
    # my_bt.fetch_data()
    # my_bt.moving_average_strategy(10, 30)  # Different parameters
    # my_bt.calculate_returns()
    # print(my_bt.get_performance_metrics())
    # my_bt.plot_results()