"""
Export Functions Module
Handles exporting forecasts and reports to Excel, PDF, and CSV formats.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
import base64


def create_excel_forecast_report(forecast_df, actual_df, metrics_dict, scenario_params=None):
    """
    Create a comprehensive Excel report with multiple sheets.
    
    Parameters:
    -----------
    forecast_df : pd.DataFrame
        DataFrame with forecast data (must have 'date' and 'forecast' columns)
    actual_df : pd.DataFrame
        DataFrame with actual data (must have 'date' and 'actual' columns)
    metrics_dict : dict
        Dictionary of metrics (MAPE, RMSE, etc.)
    scenario_params : dict, optional
        Dictionary of scenario parameters
        
    Returns:
    --------
    BytesIO : Excel file in memory
    """
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Forecast Data
        forecast_export = forecast_df.copy()
        if 'date' in forecast_export.columns:
            forecast_export['date'] = pd.to_datetime(forecast_export['date']).dt.strftime('%Y-%m-%d')
        forecast_export.to_excel(writer, sheet_name='Forecast Data', index=False)
        
        # Sheet 2: Forecast vs Actual Comparison
        # Align data properly
        min_len = min(len(actual_df), len(forecast_df))
        actual_vals = actual_df['actual'].values[:min_len] if 'actual' in actual_df.columns else actual_df.iloc[:min_len, 0].values
        forecast_vals = forecast_df['forecast'].values[:min_len] if 'forecast' in forecast_df.columns else forecast_df.iloc[:min_len, 0].values
        
        # Get dates
        if 'date' in actual_df.columns:
            dates = pd.to_datetime(actual_df['date']).values[:min_len]
        elif 'date' in forecast_df.columns:
            dates = pd.to_datetime(forecast_df['date']).values[:min_len]
        else:
            dates = pd.date_range(start='2020-01-01', periods=min_len, freq='D')
        
        comparison = pd.DataFrame({
            'Date': dates,
            'Actual': actual_vals,
            'Forecast': forecast_vals,
            'Error': actual_vals - forecast_vals,
            'Absolute Error': np.abs(actual_vals - forecast_vals),
            'Percentage Error': np.abs((actual_vals - forecast_vals) / (actual_vals + 1)) * 100
        })
        comparison['Date'] = pd.to_datetime(comparison['Date']).dt.strftime('%Y-%m-%d')
        comparison.to_excel(writer, sheet_name='Forecast vs Actual', index=False)
        
        # Sheet 3: Metrics Summary
        metrics_df = pd.DataFrame({
            'Metric': list(metrics_dict.keys()),
            'Value': [f"{v:.4f}" if isinstance(v, float) else f"{v:,.0f}" if isinstance(v, (int, np.integer)) else str(v) 
                     for v in metrics_dict.values()]
        })
        metrics_df.to_excel(writer, sheet_name='Performance Metrics', index=False)
        
        # Sheet 4: Scenario Parameters (if provided)
        if scenario_params:
            scenario_df = pd.DataFrame({
                'Parameter': list(scenario_params.keys()),
                'Value': [str(v) for v in scenario_params.values()]
            })
            scenario_df.to_excel(writer, sheet_name='Scenario Parameters', index=False)
    
    output.seek(0)
    return output


def create_csv_export(data_df, filename_prefix="forecast"):
    """
    Create CSV export from dataframe.
    
    Parameters:
    -----------
    data_df : pd.DataFrame
        DataFrame to export
    filename_prefix : str
        Prefix for filename
        
    Returns:
    --------
    str : CSV content as string
    """
    csv_string = data_df.to_csv(index=False)
    return csv_string


def get_download_link(file_content, filename, file_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
    """
    Generate download link for Streamlit.
    
    Parameters:
    -----------
    file_content : BytesIO or str
        File content
    filename : str
        Filename for download
    file_type : str
        MIME type
        
    Returns:
    --------
    str : HTML download link
    """
    if isinstance(file_content, BytesIO):
        b64 = base64.b64encode(file_content.read()).decode()
    else:
        b64 = base64.b64encode(file_content.encode()).decode()
    
    href = f'<a href="data:{file_type};base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

