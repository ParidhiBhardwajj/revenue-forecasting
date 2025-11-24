"""
Revenue Forecasting - Source Modules
"""

from .data_processing import load_data, engineer_features, get_feature_columns, split_train_test
from .modeling import train_xgboost, evaluate_model, get_feature_importance
from .visualization import (
    plot_forecast_comparison, 
    plot_residuals, 
    plot_feature_importance,
    plot_seasonality_analysis
)
from .export_functions import (
    create_excel_forecast_report,
    create_csv_export,
    get_download_link
)
from .statistical_analysis import (
    calculate_confidence_interval,
    test_promotion_impact,
    test_holiday_impact,
    calculate_correlations,
    test_stationarity,
    forecast_confidence_intervals,
    calculate_forecast_accuracy_metrics
)
from .database import ForecastDatabase

__all__ = [
    'load_data',
    'engineer_features',
    'get_feature_columns',
    'split_train_test',
    'train_xgboost',
    'evaluate_model',
    'get_feature_importance',
    'plot_forecast_comparison',
    'plot_residuals',
    'plot_feature_importance',
    'plot_seasonality_analysis',
    'create_excel_forecast_report',
    'create_csv_export',
    'get_download_link',
    'calculate_confidence_interval',
    'test_promotion_impact',
    'test_holiday_impact',
    'calculate_correlations',
    'test_stationarity',
    'forecast_confidence_intervals',
    'calculate_forecast_accuracy_metrics',
    'ForecastDatabase'
]

