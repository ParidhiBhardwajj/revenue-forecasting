"""
Data Processing Module
Handles data loading, cleaning, and feature engineering for revenue forecasting.
"""

import pandas as pd
import numpy as np


def load_data(data_path="../data/"):
    """
    Load all required datasets.
    
    Parameters:
    -----------
    data_path : str
        Path to data directory
        
    Returns:
    --------
    tuple : (sales_df, oil_df, holidays_df)
    """
    sales = pd.read_csv(f"{data_path}/train.csv", parse_dates=["date"])
    oil = pd.read_csv(f"{data_path}/oil.csv", parse_dates=["date"])
    holidays = pd.read_csv(f"{data_path}/holidays_events.csv", parse_dates=["date"])
    
    return sales, oil, holidays


def engineer_features(sales_raw, oil, holidays):
    """
    Perform feature engineering for time series forecasting.
    
    Parameters:
    -----------
    sales_raw : pd.DataFrame
        Raw sales data
    oil : pd.DataFrame
        Oil price data
    holidays : pd.DataFrame
        Holiday calendar
        
    Returns:
    --------
    pd.DataFrame : Processed dataframe with features
    """
    # Aggregate daily sales
    daily_sales = sales_raw.groupby("date")["sales"].sum().reset_index()
    promo = sales_raw.groupby("date")["onpromotion"].sum().reset_index()
    promo.rename(columns={"onpromotion": "promo_count"}, inplace=True)
    
    # Merge datasets
    df = daily_sales.merge(promo, on="date", how="left")
    df["promo_count"] = df["promo_count"].fillna(0)
    
    df = df.merge(oil, on="date", how="left")
    df["oil_price"] = df["dcoilwtico"].ffill().bfill()
    
    # Sort by date and set as index
    df = df.sort_values("date").set_index("date")
    
    # Time-based features
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day_of_week"] = df.index.dayofweek
    df["day_of_month"] = df.index.day
    df["is_weekend"] = (df.index.dayofweek >= 5).astype(int)
    df["quarter"] = df.index.quarter
    
    # Lag features
    df["lag_1"] = df["sales"].shift(1)
    df["lag_7"] = df["sales"].shift(7)
    df["lag_30"] = df["sales"].shift(30)
    
    # Rolling statistics
    df["roll_mean_7"] = df["sales"].shift(1).rolling(7).mean()
    df["roll_mean_30"] = df["sales"].shift(1).rolling(30).mean()
    df["roll_std_7"] = df["sales"].shift(1).rolling(7).std()
    df["roll_std_30"] = df["sales"].shift(1).rolling(30).std()
    
    # Holiday features
    holiday_dates = holidays["date"].dropna().unique()
    df["is_holiday"] = df.index.isin(holiday_dates).astype(int)
    
    # Year-over-year growth
    df["yoy_sales"] = df["sales"].shift(365)
    df["yoy_growth"] = (df["sales"] - df["yoy_sales"]) / (df["yoy_sales"] + 1)
    
    # Fill missing values (using forward fill then backward fill, then zero)
    df = df.bfill().ffill().fillna(0)
    
    return df


def get_feature_columns():
    """Return list of feature column names."""
    return [
        "oil_price", "promo_count", "is_holiday", "is_weekend",
        "year", "month", "day_of_week", "quarter",
        "lag_1", "lag_7", "lag_30",
        "roll_mean_7", "roll_mean_30",
        "roll_std_7", "roll_std_30"
    ]


def split_train_test(df, split_date="2017-01-01"):
    """
    Split data into training and testing sets.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Full dataset
    split_date : str
        Date to split on (YYYY-MM-DD)
        
    Returns:
    --------
    tuple : (train_df, test_df)
    """
    train = df.loc[:split_date].copy()
    test = df.loc[split_date:].copy()
    return train, test

