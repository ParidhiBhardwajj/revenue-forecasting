"""
Revenue Forecasting Dashboard
A comprehensive business intelligence dashboard for revenue forecasting and scenario analysis.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import custom modules
try:
    from src.data_processing import (
        load_data, engineer_features, get_feature_columns, split_train_test
    )
    from src.modeling import (
        train_xgboost, evaluate_model, get_feature_importance
    )
    from src.visualization import (
        plot_forecast_comparison, plot_residuals, plot_feature_importance,
        plot_seasonality_analysis
    )
    from src.export_functions import (
        create_excel_forecast_report, create_csv_export
    )
    from src.statistical_analysis import (
        calculate_confidence_interval, test_promotion_impact, test_holiday_impact,
        calculate_correlations, forecast_confidence_intervals,
        calculate_forecast_accuracy_metrics
    )
    from src.database import ForecastDatabase
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.data_processing import (
        load_data, engineer_features, get_feature_columns, split_train_test
    )
    from src.modeling import (
        train_xgboost, evaluate_model, get_feature_importance
    )
    from src.visualization import (
        plot_forecast_comparison, plot_residuals, plot_feature_importance,
        plot_seasonality_analysis
    )
    from src.export_functions import (
        create_excel_forecast_report, create_csv_export
    )
    from src.statistical_analysis import (
        calculate_confidence_interval, test_promotion_impact, test_holiday_impact,
        calculate_correlations, forecast_confidence_intervals,
        calculate_forecast_accuracy_metrics
    )
    from src.database import ForecastDatabase

# Page configuration
st.set_page_config(
    page_title="Revenue Forecast Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# DATA LOADING & PROCESSING
# ===============================
@st.cache_data
def load_and_process_data():
    """Load and process all data with caching."""
    try:
        # Get the correct data path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(os.path.dirname(script_dir), "data")
        sales_raw, oil, holidays = load_data(data_path)
        df = engineer_features(sales_raw, oil, holidays)
        return df, sales_raw
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please ensure data files are in the 'data/' directory.")
        st.stop()

# Load data
with st.spinner("Loading and processing data..."):
    df, sales_raw = load_and_process_data()

feature_cols = get_feature_columns()

# Train-test split
train, test = split_train_test(df, split_date="2017-01-01")
X_train = train[feature_cols]
y_train = train["sales"]
X_test = test[feature_cols]
y_test = test["sales"]

# ===============================
# MODEL TRAINING
# ===============================
@st.cache_resource
def get_trained_models(_X_train, _y_train, _feature_cols, test_size):
    """Train and cache models."""
    xgb_model = train_xgboost(_X_train, _y_train)
    
    # Baseline predictions using lag_1 feature
    baseline_pred = _X_train["lag_1"].values[-test_size:]
    if len(baseline_pred) < test_size:
        # Pad if needed
        baseline_pred = np.pad(baseline_pred, (0, max(0, test_size - len(baseline_pred))), 
                              mode='edge')
    baseline_pred = baseline_pred[:test_size]
    
    return xgb_model, baseline_pred

xgb_model, baseline_pred = get_trained_models(X_train, y_train, feature_cols, len(X_test))

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("🎛️ Dashboard Controls")

# Initialize Database
@st.cache_resource
def get_database(_df):
    """Initialize and return database connection."""
    db = ForecastDatabase()
    # Initialize with historical data (one-time)
    if not st.session_state.get('db_initialized', False):
        try:
            db.save_historical_sales(_df)
            st.session_state['db_initialized'] = True
        except Exception as e:
            pass  # Database may already have data
    return db

db = get_database(df)

# Navigation
page = st.sidebar.selectbox(
    "Select Page",
    ["📈 Overview", "🔮 Forecasting", "📊 Model Analysis", "📈 Statistical Analysis", "💼 Business Insights", "💾 Database"]
)

# Scenario controls (for Forecasting page)
st.sidebar.markdown("---")
st.sidebar.subheader("Scenario Parameters")

promo_change = st.sidebar.slider(
    "Promotions Change (%)", -50, 100, 0,
    help="Percentage change in promotion volume"
)
oil_change = st.sidebar.slider(
    "Oil Price Change (%)", -30, 30, 0,
    help="Percentage change in oil prices"
)
forecast_days = st.sidebar.slider(
    "Forecast Horizon (days)", 7, 90, 30,
    help="Number of days to forecast ahead"
)

# ===============================
# OVERVIEW PAGE
# ===============================
if page == "📈 Overview":
    st.markdown('<h1 class="main-header">📊 Revenue Forecasting Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = df["sales"].sum()
    avg_daily_sales = df["sales"].mean()
    peak_sales = df["sales"].max()
    peak_date = df["sales"].idxmax()
    
    with col1:
        st.metric("Total Revenue", f"${total_sales:,.0f}")
    with col2:
        st.metric("Avg Daily Sales", f"${avg_daily_sales:,.0f}")
    with col3:
        st.metric("Peak Sales Day", f"${peak_sales:,.0f}")
    with col4:
        st.metric("Date Range", f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    
    st.markdown("---")
    
    # Historical Sales Trend
    st.subheader("📈 Historical Sales Trend")
    
    fig_overview = plot_forecast_comparison(
        train.index, train["sales"],
        test.index[:forecast_days], 
        y_test[:forecast_days],
        baseline_pred[:forecast_days],
        title="Historical Sales Performance"
    )
    st.plotly_chart(fig_overview, use_container_width=True)
    
    # Seasonal Analysis
    st.subheader("🔄 Seasonality Patterns")
    fig_season = plot_seasonality_analysis(df)
    st.plotly_chart(fig_season, use_container_width=True)
    
    # Data Summary
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Dataset Summary")
        summary_stats = pd.DataFrame({
            "Metric": ["Total Records", "Date Range", "Avg Daily Sales", 
                      "Total Stores", "Product Families"],
            "Value": [
                str(len(df)),
                f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}",
                f"${avg_daily_sales:,.0f}",
                str(sales_raw["store_nbr"].nunique()),
                str(sales_raw["family"].nunique())
            ]
        })
        st.dataframe(summary_stats, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("📊 Top Product Categories")
        # Get top families by sales
        top_families = sales_raw.groupby("family")["sales"].sum().sort_values(ascending=False).head(10)
        families_df = pd.DataFrame({
            "Product Family": top_families.index,
            "Total Sales": [f"${x:,.0f}" for x in top_families.values]
        })
        st.dataframe(families_df, use_container_width=True, hide_index=True)

# ===============================
# FORECASTING PAGE
# ===============================
elif page == "🔮 Forecasting":
    st.markdown('<h1 class="main-header">🔮 Revenue Forecasting & Scenario Analysis</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Apply scenario changes
    scenario_df = X_test.copy()
    scenario_df["promo_count"] = scenario_df["promo_count"] * (1 + promo_change / 100)
    scenario_df["oil_price"] = scenario_df["oil_price"] * (1 + oil_change / 100)
    
    # Ensure lag features are properly updated (simplified for demo)
    # In production, you'd need to recalculate these based on scenario
    
    scenario_pred = xgb_model.predict(scenario_df)
    baseline_scenario = baseline_pred[:forecast_days]
    
    # Calculate business metrics
    baseline_revenue = baseline_scenario.sum()
    scenario_revenue = scenario_pred[:forecast_days].sum()
    revenue_impact = scenario_revenue - baseline_revenue
    revenue_impact_pct = (revenue_impact / baseline_revenue * 100) if baseline_revenue > 0 else 0
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Baseline Forecast",
            f"${baseline_revenue:,.0f}",
            help="Revenue forecast without scenario changes"
        )
    with col2:
        st.metric(
            "Scenario Forecast",
            f"${scenario_revenue:,.0f}",
            delta=f"${revenue_impact:,.0f} ({revenue_impact_pct:.2f}%)"
        )
    with col3:
        actual_revenue = y_test[:forecast_days].sum()
        st.metric(
            "Actual Revenue",
            f"${actual_revenue:,.0f}",
            delta=f"${scenario_revenue - actual_revenue:,.0f}"
        )
    with col4:
        mape = evaluate_model(y_test[:forecast_days], scenario_pred[:forecast_days])["MAPE"]
        st.metric(
            "Forecast Accuracy (MAPE)",
            f"{mape:.2f}%",
            help="Mean Absolute Percentage Error"
        )
    
    st.markdown("---")
    
    # Forecast Visualization
    st.subheader("📊 Forecast Comparison")
    
    fig_forecast = plot_forecast_comparison(
        train.index[-90:], train["sales"][-90:],
        test.index[:forecast_days],
        y_test[:forecast_days],
        scenario_pred[:forecast_days],
        title=f"Revenue Forecast - {forecast_days} Day Horizon"
    )
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # Export Functionality
    st.markdown("---")
    st.subheader("📥 Export Forecast")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # Prepare data for export
        forecast_export_df = pd.DataFrame({
            'date': test.index[:forecast_days],
            'forecast': scenario_pred[:forecast_days]
        })
        actual_export_df = pd.DataFrame({
            'date': test.index[:forecast_days],
            'actual': y_test[:forecast_days].values if len(y_test) >= forecast_days else y_test.values
        })
        
        metrics_export = evaluate_model(y_test[:forecast_days], scenario_pred[:forecast_days])
        scenario_params_export = {
            'Promotions Change': f"{promo_change}%",
            'Oil Price Change': f"{oil_change}%",
            'Forecast Days': forecast_days
        }
        
        # Excel Export
        excel_file = create_excel_forecast_report(
            forecast_export_df,
            actual_export_df,
            metrics_export,
            scenario_params_export
        )
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_file,
            file_name=f"forecast_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with export_col2:
        # CSV Export
        csv_data = create_csv_export(forecast_export_df, "forecast")
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"forecast_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with export_col3:
        # Save to Database
        scenario_name = f"promo_{promo_change}_oil_{oil_change}_days_{forecast_days}"
        if st.button("💾 Save Scenario to Database"):
            try:
                # Save forecasts
                forecast_save_df = pd.DataFrame({
                    'date': test.index[:forecast_days],
                    'forecast': scenario_pred[:forecast_days]
                })
                db.save_bulk_forecasts(forecast_save_df, model_type="XGBoost", scenario_name=scenario_name)
                
                # Save scenario
                db.save_scenario(scenario_name, promo_change, oil_change, forecast_days, revenue_impact)
                
                # Save model performance
                db.save_model_performance("XGBoost", mape, metrics_export.get("RMSE", 0), 
                                         metrics_export.get("MAE", 0), metrics_export.get("R2", 0))
                
                st.success(f"✅ Scenario '{scenario_name}' saved to database!")
            except Exception as e:
                st.error(f"Error saving to database: {str(e)}")
    
    # Scenario Impact Analysis
    st.markdown("---")
    st.subheader("💼 Scenario Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Revenue Impact Breakdown")
        impact_data = pd.DataFrame({
            "Metric": [
                "Baseline Revenue",
                "Scenario Revenue",
                "Revenue Impact",
                "Impact Percentage"
            ],
            "Value": [
                f"${baseline_revenue:,.0f}",
                f"${scenario_revenue:,.0f}",
                f"${revenue_impact:,.0f}",
                f"{revenue_impact_pct:.2f}%"
            ]
        })
        st.dataframe(impact_data, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Scenario Parameters")
        scenario_params = pd.DataFrame({
            "Parameter": ["Promotions Change", "Oil Price Change", "Forecast Horizon"],
            "Value": [
                f"{promo_change:+.1f}%",
                f"{oil_change:+.1f}%",
                f"{forecast_days} days"
            ]
        })
        st.dataframe(scenario_params, use_container_width=True, hide_index=True)

# ===============================
# MODEL ANALYSIS PAGE
# ===============================
elif page == "📊 Model Analysis":
    st.markdown('<h1 class="main-header">📊 Model Performance & Analysis</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Model Predictions
    xgb_pred = xgb_model.predict(X_test)
    
    # Evaluation Metrics
    xgb_metrics = evaluate_model(y_test, xgb_pred)
    baseline_metrics = evaluate_model(y_test[:len(baseline_pred)], baseline_pred)
    
    st.subheader("📈 Model Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### XGBoost Model")
        st.metric("MAPE", f"{xgb_metrics['MAPE']:.2f}%")
        st.metric("RMSE", f"${xgb_metrics['RMSE']:,.0f}")
        st.metric("R² Score", f"{xgb_metrics['R2']:.3f}")
    
    with col2:
        st.markdown("### Baseline Model (Lag-1)")
        st.metric("MAPE", f"{baseline_metrics['MAPE']:.2f}%")
        st.metric("RMSE", f"${baseline_metrics['RMSE']:,.0f}")
        st.metric("R² Score", f"{baseline_metrics['R2']:.3f}")
    
    with col3:
        st.markdown("### Improvement")
        mape_improvement = baseline_metrics['MAPE'] - xgb_metrics['MAPE']
        rmse_improvement = baseline_metrics['RMSE'] - xgb_metrics['RMSE']
        st.metric("MAPE Improvement", f"{mape_improvement:.2f}%")
        st.metric("RMSE Improvement", f"${rmse_improvement:,.0f}")
        improvement_pct = (mape_improvement / baseline_metrics['MAPE'] * 100)
        st.metric("Overall Improvement", f"{improvement_pct:.1f}%")
    
    st.markdown("---")
    
    # Feature Importance
    st.subheader("🔍 Feature Importance Analysis")
    importance_df = get_feature_importance(xgb_model, feature_cols)
    fig_importance = plot_feature_importance(importance_df, top_n=15)
    st.plotly_chart(fig_importance, use_container_width=True)
    
    # Residual Analysis
    st.subheader("🔬 Residual Analysis")
    fig_residuals = plot_residuals(y_test[:len(xgb_pred)], xgb_pred[:len(y_test)])
    st.plotly_chart(fig_residuals, use_container_width=True)
    
    # Prediction vs Actual Scatter
    st.subheader("📉 Prediction Accuracy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Detailed Metrics")
        metrics_df = pd.DataFrame({
            "Metric": list(xgb_metrics.keys()),
            "Value": [f"{v:.4f}" if isinstance(v, float) else f"{v:,.0f}" 
                     for v in xgb_metrics.values()]
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Model Statistics")
        stats_data = {
            "Training Samples": len(X_train),
            "Test Samples": len(X_test),
            "Features Used": len(feature_cols),
            "Model Type": "XGBoost Regressor"
        }
        stats_df = pd.DataFrame({
            "Statistic": list(stats_data.keys()),
            "Value": [str(v) for v in stats_data.values()]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

# ===============================
# STATISTICAL ANALYSIS PAGE
# ===============================
elif page == "📈 Statistical Analysis":
    st.markdown('<h1 class="main-header">📈 Advanced Statistical Analysis</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Promotion Impact Test
    st.subheader("📊 Statistical Significance Testing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Promotion Impact Analysis")
        promo_results = test_promotion_impact(df)
        
        if "error" not in promo_results:
            st.write(f"**Test Statistic (t):** {promo_results['t_statistic']:.4f}")
            st.write(f"**P-Value:** {promo_results['p_value']:.6f}")
            
            if promo_results['significant']:
                st.success(f"✅ **Statistically Significant** (p < 0.05)")
            else:
                st.warning(f"⚠️ **Not Statistically Significant** (p ≥ 0.05)")
            
            st.write(f"**Promotion Days Avg Sales:** ${promo_results['promo_mean']:,.0f}")
            st.write(f"**Non-Promotion Days Avg Sales:** ${promo_results['no_promo_mean']:,.0f}")
            st.write(f"**Lift:** {promo_results['lift_percentage']:.2f}%")
            st.write(f"**Effect Size (Cohen's d):** {promo_results['cohens_d']:.3f} ({promo_results['effect_size']})")
        else:
            st.error(promo_results['error'])
    
    with col2:
        st.markdown("### Holiday Impact Analysis")
        holiday_results = test_holiday_impact(df)
        
        if "error" not in holiday_results:
            st.write(f"**Test Statistic (t):** {holiday_results['t_statistic']:.4f}")
            st.write(f"**P-Value:** {holiday_results['p_value']:.6f}")
            
            if holiday_results['significant']:
                st.success(f"✅ **Statistically Significant** (p < 0.05)")
            else:
                st.warning(f"⚠️ **Not Statistically Significant** (p ≥ 0.05)")
            
            st.write(f"**Holiday Days Avg Sales:** ${holiday_results['holiday_mean']:,.0f}")
            st.write(f"**Regular Days Avg Sales:** ${holiday_results['regular_mean']:,.0f}")
            st.write(f"**Lift:** {holiday_results['lift_percentage']:.2f}%")
        else:
            st.error(holiday_results['error'])
    
    st.markdown("---")
    
    # Correlation Analysis
    st.subheader("🔗 Correlation Analysis")
    
    corr_df = calculate_correlations(df, target_col='sales', top_n=15)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display correlation table
        corr_display = corr_df.copy()
        corr_display['Correlation'] = corr_display['Correlation'].apply(lambda x: f"{x:.4f}")
        corr_display['P_Value'] = corr_display['P_Value'].apply(lambda x: f"{x:.6f}")
        corr_display['Significant'] = corr_display['Significant'].apply(lambda x: "✅ Yes" if x else "❌ No")
        st.dataframe(corr_display, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Top Correlations")
        for idx, row in corr_df.head(5).iterrows():
            significance = "✅" if row['Significant'] else "❌"
            st.write(f"{significance} **{row['Feature']}**")
            st.write(f"   r = {row['Correlation']:.3f}")
    
    st.markdown("---")
    
    # Confidence Intervals
    st.subheader("📊 Forecast Confidence Intervals")
    
    # Get predictions for confidence intervals
    xgb_pred = xgb_model.predict(X_test)
    errors = y_test[:len(xgb_pred)].values - xgb_pred[:len(y_test)]
    
    # Use a subset of predictions for demonstration
    sample_forecasts = xgb_pred[:min(forecast_days, len(xgb_pred))]
    
    forecast_with_ci = forecast_confidence_intervals(
        sample_forecasts,
        errors[:min(forecast_days, len(errors))],
        confidence=0.95
    )
    
    st.write("**95% Confidence Intervals for Forecast:**")
    st.dataframe(forecast_with_ci.style.format({
        'forecast': '${:,.0f}',
        'lower_bound': '${:,.0f}',
        'upper_bound': '${:,.0f}'
    }), use_container_width=True, hide_index=True)
    
    # Visualize confidence intervals
    import plotly.graph_objects as go
    fig_ci = go.Figure()
    
    dates = test.index[:forecast_days]
    fig_ci.add_trace(go.Scatter(
        x=dates, y=forecast_with_ci['upper_bound'],
        mode='lines', name='Upper Bound',
        line=dict(width=0), showlegend=False
    ))
    fig_ci.add_trace(go.Scatter(
        x=dates, y=forecast_with_ci['lower_bound'],
        mode='lines', name='Lower Bound',
        fill='tonexty', fillcolor='rgba(255,0,0,0.2)',
        line=dict(width=0), showlegend=False
    ))
    fig_ci.add_trace(go.Scatter(
        x=dates, y=forecast_with_ci['forecast'],
        mode='lines+markers', name='Forecast',
        line=dict(color='blue', width=2)
    ))
    
    fig_ci.update_layout(
        title="Forecast with 95% Confidence Intervals",
        xaxis_title="Date",
        yaxis_title="Sales",
        hovermode='x unified',
        template="plotly_white",
        height=500
    )
    
    st.plotly_chart(fig_ci, use_container_width=True)
    
    st.markdown("---")
    
    # Comprehensive Accuracy Metrics
    st.subheader("📈 Comprehensive Forecast Accuracy Metrics")
    
    # Use available predictions
    available_days = min(forecast_days, len(y_test), len(xgb_pred))
    comprehensive_metrics = calculate_forecast_accuracy_metrics(
        y_test[:available_days],
        xgb_pred[:available_days]
    )
    
    metrics_display = pd.DataFrame({
        'Metric': list(comprehensive_metrics.keys()),
        'Value': [f"${v:,.2f}" if 'Error' in k or 'MAE' in k or 'RMSE' in k else 
                 f"{v:.4f}" if isinstance(v, float) else str(v) 
                 for k, v in comprehensive_metrics.items()]
    })
    st.dataframe(metrics_display, use_container_width=True, hide_index=True)

# ===============================
# DATABASE PAGE
# ===============================
elif page == "💾 Database":
    st.markdown('<h1 class="main-header">💾 Database Management</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Saved Forecasts", "🎯 Scenarios", "📈 Model Performance", "🔍 Custom Query"])
    
    with tab1:
        st.subheader("Saved Forecasts")
        
        # Get scenarios safely
        try:
            scenarios_df = db.get_scenarios()
            scenario_list = ["All"]
            if len(scenarios_df) > 0 and 'scenario_name' in scenarios_df.columns:
                scenario_list.extend([s for s in scenarios_df['scenario_name'].unique() if s])
        except:
            scenario_list = ["All"]
        
        scenario_filter = st.selectbox("Filter by Scenario", scenario_list)
        
        if scenario_filter == "All":
            forecasts_df = db.get_forecasts()
        else:
            forecasts_df = db.get_forecasts(scenario_name=scenario_filter)
        
        if len(forecasts_df) > 0:
            st.dataframe(forecasts_df, use_container_width=True, hide_index=True)
            
            # Export saved forecasts
            csv_forecasts = forecasts_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Forecasts (CSV)",
                data=csv_forecasts,
                file_name=f"saved_forecasts_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No forecasts saved yet. Save a scenario from the Forecasting page.")
    
    with tab2:
        st.subheader("Saved Scenarios")
        
        scenarios_df = db.get_scenarios()
        
        if len(scenarios_df) > 0:
            st.dataframe(scenarios_df, use_container_width=True, hide_index=True)
        else:
            st.info("No scenarios saved yet.")
    
    with tab3:
        st.subheader("Model Performance History")
        
        perf_df = db.get_model_performance_history()
        
        if len(perf_df) > 0:
            st.dataframe(perf_df, use_container_width=True, hide_index=True)
            
            # Visualize performance over time
            if len(perf_df) > 1:
                import plotly.express as px
                fig_perf = px.line(perf_df, x='created_at', y='mape', 
                                  title='Model MAPE Over Time',
                                  markers=True)
                st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("No model performance data saved yet.")
    
    with tab4:
        st.subheader("Custom SQL Query")
        
        query = st.text_area("Enter SQL Query", height=150,
                            value="SELECT * FROM forecasts LIMIT 10")
        
        if st.button("Execute Query"):
            try:
                result_df = db.execute_query(query)
                st.dataframe(result_df, use_container_width=True, hide_index=True)
                st.success(f"Query executed successfully! Returned {len(result_df)} rows.")
            except Exception as e:
                st.error(f"Query error: {str(e)}")
        
        st.markdown("### Available Tables:")
        st.code("""
- forecasts (date, forecast_value, actual_value, model_type, scenario_name)
- scenarios (scenario_name, promo_change, oil_change, forecast_days, revenue_impact)
- model_performance (model_type, mape, rmse, mae, r2_score, test_date)
- historical_sales (date, sales, promo_count, oil_price, is_holiday)
        """)

# ===============================
# BUSINESS INSIGHTS PAGE
# ===============================
elif page == "💼 Business Insights":
    st.markdown('<h1 class="main-header">💼 Business Intelligence & Insights</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key Business Metrics
    st.subheader("💰 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate YoY growth
    df_with_yoy = df.copy()
    df_with_yoy["year"] = df_with_yoy.index.year
    yearly_sales = df_with_yoy.groupby("year")["sales"].sum()
    
    if len(yearly_sales) > 1:
        yoy_growth = ((yearly_sales.iloc[-1] - yearly_sales.iloc[-2]) / yearly_sales.iloc[-2] * 100)
    else:
        yoy_growth = 0
    
    with col1:
        st.metric("Total Revenue", f"${df['sales'].sum():,.0f}")
    with col2:
        st.metric("Avg Daily Revenue", f"${df['sales'].mean():,.0f}")
    with col3:
        st.metric("YoY Growth", f"{yoy_growth:.1f}%")
    with col4:
        st.metric("Peak Daily Revenue", f"${df['sales'].max():,.0f}")
    
    st.markdown("---")
    
    # Seasonal Insights
    st.subheader("📅 Seasonal Pattern Insights")
    
    df_insights = df.copy()
    df_insights["month_name"] = df_insights.index.strftime("%B")
    df_insights["day_name"] = df_insights.index.strftime("%A")
    
    monthly_avg = df_insights.groupby("month_name")["sales"].mean().sort_values(ascending=False)
    weekly_avg = df_insights.groupby("day_name")["sales"].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top Performing Months")
        top_months = pd.DataFrame({
            "Month": monthly_avg.index[:6],
            "Avg Daily Sales": [f"${x:,.0f}" for x in monthly_avg.values[:6]]
        })
        st.dataframe(top_months, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Weekly Pattern")
        weekly_df = pd.DataFrame({
            "Day": weekly_avg.index,
            "Avg Daily Sales": [f"${x:,.0f}" for x in weekly_avg.values]
        })
        st.dataframe(weekly_df, use_container_width=True, hide_index=True)
    
    # Business Recommendations
    st.markdown("---")
    st.subheader("💡 Business Recommendations")
    
    # Analyze promotion impact
    promo_impact = df.groupby(df["promo_count"] > 0)["sales"].mean()
    if len(promo_impact) == 2:
        promo_boost = ((promo_impact[True] - promo_impact[False]) / promo_impact[False] * 100)
        st.info(f"📈 **Promotion Impact**: Days with promotions show {promo_boost:.1f}% higher average sales compared to non-promotion days.")
    
    # Holiday impact
    holiday_impact = df.groupby("is_holiday")["sales"].mean()
    if len(holiday_impact) == 2:
        holiday_boost = ((holiday_impact[1] - holiday_impact[0]) / holiday_impact[0] * 100)
        st.info(f"🎉 **Holiday Impact**: Sales during holidays are {holiday_boost:.1f}% higher than regular days.")
    
    # Oil price correlation
    if "oil_price" in df.columns and df["oil_price"].notna().any():
        oil_corr = df["sales"].corr(df["oil_price"])
        st.info(f"⛽ **Oil Price Correlation**: Sales show a correlation of {oil_corr:.3f} with oil prices. "
                f"{'Negative correlation suggests oil prices may impact sales.' if oil_corr < 0 else 'Positive correlation suggests higher oil prices may coincide with higher sales.'}")
    
    # Peak sales analysis
    peak_months = monthly_avg.head(3).index.tolist()
    st.success(f"🎯 **Strategic Insight**: Top performing months are {', '.join(peak_months)}. "
               "Consider increasing inventory and marketing efforts during these periods.")

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "Built with Streamlit • Revenue Forecasting Dashboard • "
    "Demonstrating Data Analytics & Machine Learning Expertise"
    "</div>",
    unsafe_allow_html=True
)
