"""
Modeling Module
Handles machine learning model training, evaluation, and prediction.
"""

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from prophet import Prophet
from sklearn.metrics import (
    mean_absolute_percentage_error,
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
import warnings
warnings.filterwarnings('ignore')


def train_xgboost(X_train, y_train, **kwargs):
    """
    Train XGBoost model.
    
    Parameters:
    -----------
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training target
    **kwargs : dict
        Additional XGBoost parameters
        
    Returns:
    --------
    XGBRegressor : Trained model
    """
    default_params = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "n_jobs": -1
    }
    default_params.update(kwargs)
    
    model = XGBRegressor(**default_params)
    model.fit(X_train, y_train)
    return model


def train_prophet(df_train, df_test=None):
    """
    Train Prophet model for time series forecasting.
    
    Parameters:
    -----------
    df_train : pd.DataFrame
        Training data with 'ds' (date) and 'y' (target) columns
    df_test : pd.DataFrame, optional
        Test data for evaluation
        
    Returns:
    --------
    Prophet : Trained model
    """
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        changepoint_prior_scale=0.05
    )
    
    # Add holiday effects if available
    model.fit(df_train)
    return model


def evaluate_model(y_true, y_pred):
    """
    Calculate comprehensive model evaluation metrics.
    
    Parameters:
    -----------
    y_true : array-like
        True values
    y_pred : array-like
        Predicted values
        
    Returns:
    --------
    dict : Dictionary of metrics
    """
    metrics = {
        "MAPE": mean_absolute_percentage_error(y_true, y_pred) * 100,
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "R2": r2_score(y_true, y_pred),
        "Mean_Actual": np.mean(y_true),
        "Mean_Predicted": np.mean(y_pred)
    }
    
    # Additional business metrics
    metrics["Error_Percentage"] = abs(metrics["Mean_Predicted"] - metrics["Mean_Actual"]) / metrics["Mean_Actual"] * 100
    
    return metrics


def get_feature_importance(model, feature_names):
    """
    Extract feature importance from trained model.
    
    Parameters:
    -----------
    model : XGBRegressor
        Trained XGBoost model
    feature_names : list
        List of feature names
        
    Returns:
    --------
    pd.DataFrame : Feature importance dataframe
    """
    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
    
    return importance_df

