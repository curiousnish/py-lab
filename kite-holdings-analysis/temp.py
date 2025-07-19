#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from nsepython import *
#%%
# Load holdings data
file_path = 'holdings.csv'  # replace with your file path
df = pd.read_csv(file_path)
#%%
# Ensure numeric columns
df['Qty.'] = pd.to_numeric(df['Qty.'], errors='coerce')
df['Avg. cost'] = pd.to_numeric(df['Avg. cost'], errors='coerce')
df['LTP'] = pd.to_numeric(df['LTP'], errors='coerce')
#%%
# Calculate Invested Value and Current Value
df['Invested Value'] = df['Qty.'] * df['Avg. cost']
df['Current Value'] = df['Qty.'] * df['LTP']
df['Unrealised P&L'] = df['Current Value'] - df['Invested Value']
df['% Return'] = (df['Unrealised P&L'] / df['Invested Value']) * 100
#%%
# 1. Portfolio Allocation Analysis
total_current_value = df['Current Value'].sum()
df['Portfolio Allocation %'] = (df['Current Value'] / total_current_value) * 100
df_sorted = df.sort_values('Portfolio Allocation %')

plt.figure(figsize=(8,8))
# plt.pie(df['Portfolio Allocation %'], labels=df['Instrument'], autopct='%1.1f%%')
plt.barh(df_sorted['Instrument'], df_sorted['Portfolio Allocation %'], color='skyblue')
plt.title('Portfolio Allocation by Stock')
plt.tight_layout()
plt.show()
#%%
# 2. Unrealised Gains & Losses
print("\nTop Gainers:")
print(df.sort_values(by='Unrealised P&L', ascending=False)[['Symbol', 'Unrealised P&L', '% Return']].head())

print("\nTop Losers:")
print(df.sort_values(by='Unrealised P&L')[['Symbol', 'Unrealised P&L', '% Return']].head())

# 3. Diversification Analysis
num_stocks = df['Symbol'].nunique()
print(f"\nNumber of unique stocks held: {num_stocks}")

hhi = (df['Portfolio Allocation %'] ** 2).sum()
print(f"Portfolio HHI (Concentration Index): {hhi:.2f}")

# 4. Investment Cost Analysis
total_invested = df['Invested Value'].sum()
total_unrealised_pl = df['Unrealised P&L'].sum()
total_return_percent = (total_unrealised_pl / total_invested) * 100

print(f"\nTotal Invested Amount: ₹{total_invested:,.2f}")
print(f"Current Market Value: ₹{total_current_value:,.2f}")
print(f"Total Unrealised P&L: ₹{total_unrealised_pl:,.2f} ({total_return_percent:.2f}%)")

# 5. Time-Based Performance Tracking
# For demo, simulate with current data
# Maintain daily snapshots in a database or CSV to plot over time.

print("\nFor time-based tracking, store daily snapshots to build a performance graph.")

# 6. Dividend Yield Analysis using nsepython
dividend_yields = []
for symbol in df['Symbol']:
    try:
        quote = nse_quote(symbol)
        div_yield = float(quote['data'][0].get('divYield', '0').replace('%',''))
        dividend_yields.append(div_yield)
    except Exception as e:
        dividend_yields.append(np.nan)

df['Dividend Yield %'] = dividend_yields
df['Estimated Annual Dividend'] = (df['Current Value'] * df['Dividend Yield %']) / 100
print("\nDividend Yield Analysis:")
print(df[['Symbol', 'Dividend Yield %', 'Estimated Annual Dividend']])

# 7. Risk Exposure Analysis - Beta from NSEPython
betas = []
for symbol in df['Symbol']:
    try:
        quote = nse_quote(symbol)
        beta = float(quote['data'][0].get('beta', '0'))
        betas.append(beta)
    except Exception as e:
        betas.append(np.nan)

df['Beta'] = betas
df['Weighted Beta'] = df['Beta'] * (df['Portfolio Allocation %'] / 100)
portfolio_beta = df['Weighted Beta'].sum()
print(f"\nPortfolio Beta (Market risk exposure): {portfolio_beta:.2f}")

# 8. Rebalancing & Optimization Analysis
# Example: equal weight strategy suggestion
equal_weight = 100 / num_stocks
df['Rebalance Diff %'] = df['Portfolio Allocation %'] - equal_weight
print("\nRebalancing Suggestions (Positive=overweight, Negative=underweight):")
print(df[['Symbol', 'Portfolio Allocation %', 'Rebalance Diff %']])

# 9. Scenario & Sensitivity Analysis
# Example: impact of 5% market correction
df['-5% Correction Impact'] = df['Current Value'] * -0.05
portfolio_impact = df['-5% Correction Impact'].sum()
print(f"\nEstimated Portfolio Loss in -5% Correction: ₹{portfolio_impact:,.2f}")

# 10. Tax Optimization Analysis
# Assuming you track holding period, calculate LTCG vs STCG eligibility

# BONUS: NSE Integration for Sector and Market Cap
sectors = []
market_caps = []

for symbol in df['Symbol']:
    try:
        quote = nse_quote(symbol)
        sector = quote['metadata']['sector']
        mcap = quote['metadata']['marketCap']
        sectors.append(sector)
        market_caps.append(mcap)
    except Exception as e:
        sectors.append('NA')
        market_caps.append('NA')

df['Sector'] = sectors
df['Market Cap'] = market_caps

# Sector-wise allocation analysis
sector_allocation = df.groupby('Sector')['Current Value'].sum()
sector_allocation_percent = (sector_allocation / total_current_value) * 100

print("\nSector Allocation (%):")
print(sector_allocation_percent)

sector_allocation_percent.plot(kind='bar', title='Portfolio Sector Allocation (%)', figsize=(10,5))
plt.ylabel('Allocation %')
plt.tight_layout()
plt.show()

# Save updated dataframe to CSV for records
df.to_csv('holdings_analysis_output.csv', index=False)

print("\n✅ All analyses completed and saved to holdings_analysis_output.csv")
