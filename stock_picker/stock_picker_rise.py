from globals import *
import pandas as pd
import numpy as np
import yfinance as yf
from ta import add_all_ta_features
from ta.utils import dropna
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from stock_picker_tickers import SP500_TICKERS
import os

# Constants
LOOKBACK_PERIOD = 30  # Days for historical data
PREDICTION_DAYS = 1  # Days to predict
VALIDATION_DATE = STOCK_PICKER_VALIDATION_DATE
TRAINING_START_DATE = TRAINING_PERIOD_STOCKPICK_START
TRAINING_END_DATE = training_period_end
VALIDATE = True

def fetch_data(ticker, start_date=TRAINING_START_DATE, end_date=None):
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            print(f"No data found for {ticker} from {start_date} to {end_date}")
        else:
            df['Ticker'] = ticker
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def engineer_features(df):
    df = dropna(df)
    
    # Check if there's enough data for feature engineering
    if len(df) < 30:  # Adjust based on the maximum window size used by indicators
        print("Not enough data to calculate technical indicators.")
        return pd.DataFrame()
    
    try:
        df = add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
    except Exception as e:
        print(f"Error adding technical indicators: {e}")
        return pd.DataFrame()
    
    # Ensure there are no non-numeric columns
    df = df.select_dtypes(include=[np.number])
    
    df['Return'] = df['Close'].pct_change()
    df['Target'] = (df['Return'].shift(-PREDICTION_DAYS) > 0).astype(int)
    df = df.dropna()
    
    return df

def prepare_data(tickers):
    all_data = []
    for ticker in tickers:
        df = fetch_data(ticker)
        if not df.empty:
            df = engineer_features(df)
            if df.empty:
                continue
            all_data.append(df)
    
    # Concatenate all data and drop rows with NaN values
    combined_df = pd.concat(all_data)
    combined_df = combined_df.dropna()
    
    # Ensure target column exists and separate features and target
    if 'Target' not in combined_df.columns:
        raise ValueError("Target column is missing in the data.")
    
    X = combined_df.drop(['Target'], axis=1)
    y = combined_df['Target']
    
    return X, y

def train_model(X, y):
    X = X.apply(pd.to_numeric, errors='coerce')  # Convert all columns to numeric, coerce errors to NaN
    X = X.dropna()  # Drop rows with NaN values if any
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    
    print(f"Model Accuracy: {accuracy_score(y_test, predictions):.2f}")
    return model, X.columns

def predict_and_rank(tickers, model, feature_names):
    results = []
    for ticker in tickers:
        df = fetch_data(ticker)
        if not df.empty:
            df = engineer_features(df)
            df = df.iloc[-1:]  # Use the most recent data point
            if df.empty:
                continue
            
            # Ensure the prediction DataFrame has the same columns as the training data
            X = df[feature_names]
            X = X.reindex(columns=feature_names, fill_value=0)  # Reindex to match training feature names
            pred = model.predict(X)
            results.append((ticker, pred[0]))
    
    results_df = pd.DataFrame(results, columns=['Ticker', 'Prediction'])
    results_df = results_df.sort_values(by='Prediction', ascending=False)
    results_df.to_csv(os.path.abspath(os.getcwd())+'/Stock_rise.csv')
    return results_df

def validate_predictions(tickers, model, start_date, end_date):
    results = []
    
    for ticker in tickers:
        # Fetch historical data for feature calculation
        historical_df = fetch_data(ticker, start_date=start_date, end_date=end_date)
        if historical_df.empty:
            continue

        # Engineer features on historical data
        historical_df = engineer_features(historical_df)
        if historical_df.empty:
            continue
        
        # Make predictions for each day
        for i in range(len(historical_df) - 1):
            day_data = historical_df.iloc[i:i+1]
            next_day_data = historical_df.iloc[i+1:i+2]
            
            if next_day_data.empty:
                continue

            # Prepare feature data for the prediction
            X_latest = day_data.drop(['Target'], axis=1, errors='ignore')
            X_latest = X_latest.reindex(columns=feature_names, fill_value=0)
            
            # Predict the movement using the trained model
            prediction = model.predict(X_latest)[0]
            
            # Extract the actual movement on the next day
            actual_movement = (next_day_data['Return'].iloc[0] > 0).astype(int)
            
            # Append the results
            results.append((ticker, prediction, actual_movement))
    
    results_df = pd.DataFrame(results, columns=['Ticker', 'Prediction', 'Actual'])
    results_df['Correct'] = results_df['Prediction'] == results_df['Actual']
    accuracy = results_df['Correct'].mean()
    print(f"Validation Accuracy: {accuracy:.2f}")
    return results_df

if __name__ == "__main__":
    print("Preparing data...")
    X, y = prepare_data(SP500_TICKERS)
    
    print("Training model...")
    model, feature_names = train_model(X, y)
    
    print("Predicting and ranking stocks...")
    ranked_stocks = predict_and_rank(SP500_TICKERS, model, feature_names)
    print(ranked_stocks)
    
    if VALIDATE:
        print("Validating model with unseen data...")
        validation_results = validate_predictions(SP500_TICKERS, model, start_date=TRAINING_START_DATE, end_date=TRAINING_END_DATE)
        print(validation_results)
