"""
Visualization Module
Creates professional charts and visualizations for the dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
try:
    from scipy import stats
except ImportError:
    stats = None


def plot_forecast_comparison(train_dates, train_values, test_dates, 
                            actual_values, predicted_values, title="Revenue Forecast"):
    """
    Create interactive forecast comparison plot.
    
    Parameters:
    -----------
    train_dates : array-like
        Training period dates
    train_values : array-like
        Training period values
    test_dates : array-like
        Test period dates
    actual_values : array-like
        Actual test values
    predicted_values : array-like
        Predicted test values
    title : str
        Plot title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Training data
    fig.add_trace(go.Scatter(
        x=train_dates,
        y=train_values,
        name="Training Data",
        line=dict(color="#1f77b4", width=1),
        opacity=0.6
    ))
    
    # Actual test data
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=actual_values,
        name="Actual",
        line=dict(color="#000000", width=2),
        mode='lines+markers'
    ))
    
    # Predicted
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=predicted_values,
        name="Forecast",
        line=dict(color="#ff7f0e", width=2, dash='dash'),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        xaxis_title="Date",
        yaxis_title="Sales",
        hovermode='x unified',
        template="plotly_white",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_residuals(actual, predicted, title="Residual Analysis"):
    """
    Create residual analysis plot.
    
    Parameters:
    -----------
    actual : array-like
        Actual values
    predicted : array-like
        Predicted values
    title : str
        Plot title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    residuals = actual - predicted
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Residuals Over Time", "Residual Distribution", 
                       "Actual vs Predicted", "Q-Q Plot"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Residuals over time
    fig.add_trace(
        go.Scatter(x=list(range(len(residuals))), y=residuals, mode='markers',
                  marker=dict(color='blue', size=4)),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
    
    # Residual distribution
    fig.add_trace(
        go.Histogram(x=residuals, nbinsx=30, marker_color='blue'),
        row=1, col=2
    )
    
    # Actual vs Predicted
    fig.add_trace(
        go.Scatter(x=actual, y=predicted, mode='markers',
                  marker=dict(color='green', size=4)),
        row=2, col=1
    )
    # Perfect prediction line
    min_val = min(min(actual), min(predicted))
    max_val = max(max(actual), max(predicted))
    fig.add_trace(
        go.Scatter(x=[min_val, max_val], y=[min_val, max_val],
                  mode='lines', line=dict(color='red', dash='dash')),
        row=2, col=1
    )
    
    # Q-Q plot (simplified)
    if stats is not None:
        try:
            qq = stats.probplot(residuals, dist="norm")
            fig.add_trace(
                go.Scatter(x=qq[0][0], y=qq[0][1], mode='markers',
                          marker=dict(color='purple', size=4)),
                row=2, col=2
            )
            fig.add_trace(
                go.Scatter(x=qq[0][0], y=qq[1][1] + qq[1][0] * qq[0][0],
                          mode='lines', line=dict(color='red')),
                row=2, col=2
            )
        except:
            # If Q-Q plot fails, show empty subplot
            pass
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        height=700,
        showlegend=False,
        template="plotly_white"
    )
    
    fig.update_xaxes(title_text="Index", row=1, col=1)
    fig.update_yaxes(title_text="Residuals", row=1, col=1)
    fig.update_xaxes(title_text="Residuals", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)
    fig.update_xaxes(title_text="Actual", row=2, col=1)
    fig.update_yaxes(title_text="Predicted", row=2, col=1)
    
    return fig


def plot_feature_importance(importance_df, top_n=15):
    """
    Create feature importance bar chart.
    
    Parameters:
    -----------
    importance_df : pd.DataFrame
        DataFrame with 'feature' and 'importance' columns
    top_n : int
        Number of top features to show
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    df_top = importance_df.head(top_n).sort_values("importance", ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_top["importance"],
        y=df_top["feature"],
        orientation='h',
        marker=dict(color=df_top["importance"], colorscale="Viridis"),
        text=[f"{x:.3f}" for x in df_top["importance"]],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text="Top Feature Importance", font=dict(size=18)),
        xaxis_title="Importance Score",
        yaxis_title="Feature",
        height=max(400, top_n * 30),
        template="plotly_white"
    )
    
    return fig


def plot_seasonality_analysis(df):
    """
    Analyze and plot seasonal patterns.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with date index and sales column
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    df_analysis = df.copy()
    df_analysis["month"] = df_analysis.index.month
    df_analysis["day_of_week"] = df_analysis.index.dayofweek
    df_analysis["week"] = df_analysis.index.isocalendar().week
    
    # Monthly pattern
    monthly = df_analysis.groupby("month")["sales"].mean()
    
    # Weekly pattern
    weekly = df_analysis.groupby("day_of_week")["sales"].mean()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Average Sales by Month", "Average Sales by Day of Week")
    )
    
    fig.add_trace(
        go.Bar(x=monthly.index, y=monthly.values, marker_color="steelblue"),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=weekly.index, y=weekly.values, marker_color="coral"),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Month", row=1, col=1, dtick=1)
    fig.update_xaxes(title_text="Day of Week (0=Mon)", row=1, col=2, dtick=1)
    fig.update_yaxes(title_text="Average Sales", row=1, col=1)
    fig.update_yaxes(title_text="Average Sales", row=1, col=2)
    
    fig.update_layout(
        title=dict(text="Seasonality Analysis", font=dict(size=18)),
        height=400,
        template="plotly_white",
        showlegend=False
    )
    
    return fig

