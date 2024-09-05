import yfinance as yf
import pandas as pd
from stock_picker_tickers import SP500_TICKERS

# Define a function to get fundamental data
def get_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        'Ticker': ticker,
        'PE Ratio': info.get('forwardEps', float('nan')) / info.get('forwardEps', float('nan')),
        'P/B Ratio': info.get('priceToBook', float('nan')),
        'Dividend Yield': info.get('dividendYield', float('nan')),
        'ROE': info.get('returnOnEquity', float('nan')),
        'Current Ratio': info.get('currentRatio', float('nan')),
        'Debt-to-Equity Ratio': info.get('debtToEquity', float('nan'))
    }

# List of stock tickers to analyze
tickers = SP500_TICKERS

# Collect data for each ticker
data = [get_fundamentals(ticker) for ticker in tickers]

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Handle missing values
df.fillna(0, inplace=True)

# Ranking stocks based on fundamental indicators
# Assuming lower PE Ratio, lower P/B Ratio, higher Dividend Yield, higher ROE,
# higher Current Ratio, and lower Debt-to-Equity Ratio are better

# Normalize the indicators to be on a similar scale for scoring
df['Normalized PE Ratio'] = df['PE Ratio'].max() - df['PE Ratio']
df['Normalized P/B Ratio'] = df['P/B Ratio'].max() - df['P/B Ratio']
df['Normalized Dividend Yield'] = df['Dividend Yield']
df['Normalized ROE'] = df['ROE']
df['Normalized Current Ratio'] = df['Current Ratio']
df['Normalized Debt-to-Equity Ratio'] = df['Debt-to-Equity Ratio'].max() - df['Debt-to-Equity Ratio']

# Calculate the total score
df['Score'] = (
    df['Normalized PE Ratio'] +
    df['Normalized P/B Ratio'] +
    df['Normalized Dividend Yield'] +
    df['Normalized ROE'] +
    df['Normalized Current Ratio'] +
    df['Normalized Debt-to-Equity Ratio']
)

# Sort stocks by the score in descending order
df_sorted = df.sort_values(by='Score', ascending=False)

# Print the sorted DataFrame
print(df_sorted[['Ticker', 'PE Ratio', 'P/B Ratio', 'Dividend Yield', 'ROE', 'Current Ratio', 'Debt-to-Equity Ratio', 'Score']])
