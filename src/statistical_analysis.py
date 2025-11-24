"""
Statistical Analysis Module
Provides advanced statistical analysis including hypothesis testing, confidence intervals,
and correlation analysis.
"""

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
import warnings
warnings.filterwarnings('ignore')


def calculate_confidence_interval(values, confidence=0.95):
    """
    Calculate confidence interval for a series of values.
    
    Parameters:
    -----------
    values : array-like
        Values to calculate CI for
    confidence : float
        Confidence level (default 0.95 for 95% CI)
        
    Returns:
    --------
    tuple : (lower_bound, upper_bound, mean, std_error)
    """
    values = np.array(values)
    mean = np.mean(values)
    std_err = stats.sem(values)
    h = std_err * stats.t.ppf((1 + confidence) / 2, len(values) - 1)
    
    return mean - h, mean + h, mean, std_err


def test_promotion_impact(df):
    """
    Test if promotions significantly impact sales using t-test.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with 'sales' and 'promo_count' columns
        
    Returns:
    --------
    dict : Statistical test results
    """
    # Create binary promotion indicator
    promo_days = df[df['promo_count'] > 0]['sales']
    no_promo_days = df[df['promo_count'] == 0]['sales']
    
    if len(promo_days) == 0 or len(no_promo_days) == 0:
        return {"error": "Insufficient data for comparison"}
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(promo_days, no_promo_days)
    
    # Calculate effect size (Cohen's d)
    pooled_std = np.sqrt(((len(promo_days) - 1) * promo_days.std()**2 + 
                          (len(no_promo_days) - 1) * no_promo_days.std()**2) / 
                         (len(promo_days) + len(no_promo_days) - 2))
    cohens_d = (promo_days.mean() - no_promo_days.mean()) / pooled_std
    
    # Calculate means
    promo_mean = promo_days.mean()
    no_promo_mean = no_promo_days.mean()
    lift = ((promo_mean - no_promo_mean) / no_promo_mean) * 100
    
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "promo_mean": promo_mean,
        "no_promo_mean": no_promo_mean,
        "lift_percentage": lift,
        "cohens_d": cohens_d,
        "effect_size": "large" if abs(cohens_d) > 0.8 else "medium" if abs(cohens_d) > 0.5 else "small"
    }


def test_holiday_impact(df):
    """
    Test if holidays significantly impact sales using t-test.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with 'sales' and 'is_holiday' columns
        
    Returns:
    --------
    dict : Statistical test results
    """
    holiday_days = df[df['is_holiday'] == 1]['sales']
    regular_days = df[df['is_holiday'] == 0]['sales']
    
    if len(holiday_days) == 0:
        return {"error": "No holiday data available"}
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(holiday_days, regular_days)
    
    # Calculate means and lift
    holiday_mean = holiday_days.mean()
    regular_mean = regular_days.mean()
    lift = ((holiday_mean - regular_mean) / regular_mean) * 100 if regular_mean > 0 else 0
    
    return {
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "holiday_mean": holiday_mean,
        "regular_mean": regular_mean,
        "lift_percentage": lift
    }


def calculate_correlations(df, target_col='sales', top_n=10):
    """
    Calculate correlations with target variable.
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with numeric columns
    target_col : str
        Target column name
    top_n : int
        Number of top correlations to return
        
    Returns:
    --------
    pd.DataFrame : Correlation results with p-values
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col != target_col]
    
    correlations = []
    p_values = []
    
    for col in numeric_cols:
        if df[col].notna().sum() > 10:  # Minimum data points
            corr, p_val = stats.pearsonr(df[target_col].dropna(), df[col].dropna())
            correlations.append(corr)
            p_values.append(p_val)
        else:
            correlations.append(np.nan)
            p_values.append(np.nan)
    
    corr_df = pd.DataFrame({
        'Feature': numeric_cols,
        'Correlation': correlations,
        'P_Value': p_values,
        'Significant': [p < 0.05 for p in p_values],
        'Strength': [abs(c) if not np.isnan(c) else 0 for c in correlations]
    }).sort_values('Strength', ascending=False).head(top_n)
    
    return corr_df


def test_stationarity(series, alpha=0.05):
    """
    Test time series stationarity using Augmented Dickey-Fuller test.
    
    Parameters:
    -----------
    series : pd.Series
        Time series data
    alpha : float
        Significance level
        
    Returns:
    --------
    dict : Test results
    """
    try:
        result = adfuller(series.dropna())
        adf_statistic = result[0]
        p_value = result[1]
        is_stationary = p_value < alpha
        
        return {
            "adf_statistic": adf_statistic,
            "p_value": p_value,
            "is_stationary": is_stationary,
            "critical_values": result[4],
            "interpretation": "Stationary" if is_stationary else "Non-stationary"
        }
    except Exception as e:
        return {"error": str(e)}


def forecast_confidence_intervals(forecasts, historical_errors, confidence=0.95):
    """
    Calculate confidence intervals for forecasts based on historical errors.
    
    Parameters:
    -----------
    forecasts : array-like
        Forecasted values
    historical_errors : array-like
        Historical forecast errors
    confidence : float
        Confidence level
        
    Returns:
    --------
    pd.DataFrame : Forecasts with confidence intervals
    """
    forecasts = np.array(forecasts)
    historical_errors = np.array(historical_errors)
    
    # Calculate error distribution statistics
    error_std = np.std(historical_errors)
    error_mean = np.mean(historical_errors)
    
    # Calculate confidence interval width
    z_score = stats.norm.ppf((1 + confidence) / 2)
    margin = z_score * error_std
    
    # Create dataframe with intervals
    result_df = pd.DataFrame({
        'forecast': forecasts,
        'lower_bound': forecasts - margin,
        'upper_bound': forecasts + margin,
        'confidence_level': confidence
    })
    
    return result_df


def calculate_forecast_accuracy_metrics(actual, predicted):
    """
    Calculate comprehensive forecast accuracy metrics.
    
    Parameters:
    -----------
    actual : array-like
        Actual values
    predicted : array-like
        Predicted values
        
    Returns:
    --------
    dict : Comprehensive metrics
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    errors = actual - predicted
    abs_errors = np.abs(errors)
    pct_errors = abs_errors / (actual + 1) * 100
    
    metrics = {
        "MAE": np.mean(abs_errors),
        "RMSE": np.sqrt(np.mean(errors**2)),
        "MAPE": np.mean(pct_errors),
        "Mean_Error": np.mean(errors),
        "Std_Error": np.std(errors),
        "Max_Error": np.max(abs_errors),
        "Min_Error": np.min(abs_errors),
        "Median_Abs_Error": np.median(abs_errors)
    }
    
    # Add confidence intervals for accuracy
    ci_lower, ci_upper, mean_err, std_err = calculate_confidence_interval(errors)
    metrics["Error_CI_Lower"] = ci_lower
    metrics["Error_CI_Upper"] = ci_upper
    
    return metrics

