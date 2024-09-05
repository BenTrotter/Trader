import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from stock_picker_tickers import SP500_TICKERS


# Define a function to fetch fundamental data
def fetch_fundamental_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Use default values if data is missing
        data = {
            'ticker': ticker,
            'pe_ratio': info.get('forwardEps', 0),
            'market_cap': info.get('marketCap', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'price_to_book': info.get('priceToBook', 0),
            'earnings_growth': info.get('earningsGrowth', 0)
        }
        
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# Fetch data for all tickers
def fetch_all_data(tickers):
    data = []
    for ticker in tickers:
        fundamental_data = fetch_fundamental_data(ticker)
        if fundamental_data:
            data.append(fundamental_data)
    return pd.DataFrame(data)

# Load fundamental data
df = fetch_all_data(SP500_TICKERS)

# Check if DataFrame is empty
if df.empty:
    print("No data fetched. Please check the tickers or data source.")
else:
    # Print the fetched data for inspection
    print("Fetched Data:")
    print(df[['ticker', 'price_to_book']])

    # Determine appropriate threshold based on data inspection
    min_price_to_book = df['price_to_book'].min()
    max_price_to_book = df['price_to_book'].max()
    threshold = (min_price_to_book + max_price_to_book) / 2  # Example: midpoint of min and max
    print(f"\nMinimum price_to_book: {min_price_to_book:.2f}")
    print(f"Maximum price_to_book: {max_price_to_book:.2f}")
    print(f"Using threshold: {threshold:.2f}")

    # Preprocess the data
    def preprocess_data(df):
        df = df.dropna()
        X = df[['pe_ratio', 'market_cap', 'dividend_yield', 'price_to_book', 'earnings_growth']]
        
        # Example target: Adjusted threshold
        y = (df['price_to_book'] > threshold).astype(int)
        
        # Check class balance
        print(f"\nClass distribution based on threshold {threshold:.2f}:")
        print(y.value_counts())

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y

    X, y = preprocess_data(df)

    # Check if y contains more than one class
    if y.nunique() <= 1:
        print("Error: Target variable 'y' contains only one class. Model cannot be trained.")
    else:
        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a simple model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        # Predict on test data
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nModel Accuracy: {accuracy:.2f}")

        # Predict probabilities for all stocks
        y_prob = model.predict_proba(X)
        if y_prob.shape[1] > 1:
            df['predicted_prob'] = y_prob[:, 1]
        else:
            print("Error: Model only predicts one class. Cannot retrieve probabilities.")

        # Rank stocks based on predicted probabilities
        df_sorted = df.sort_values(by='predicted_prob', ascending=False)
        df_sorted = df_sorted[['ticker', 'predicted_prob']]

        # Output the ranked list of stocks
        print("\nTop 10 Stocks Based on Predicted Probabilities:")
        print(df_sorted.head(10))
