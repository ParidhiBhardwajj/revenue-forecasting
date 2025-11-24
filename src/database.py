"""
Database Module
Handles SQLite database operations for storing forecasts, scenarios, and historical data.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import os


class ForecastDatabase:
    """
    SQLite database wrapper for storing forecasting data.
    """
    
    def __init__(self, db_path="forecast_data.db"):
        """
        Initialize database connection.
        
        Parameters:
        -----------
        db_path : str
            Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()
    
    def _get_connection(self):
        """
        Get a database connection. Creates a new connection each time
        to avoid thread-safety issues with Streamlit.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Table 1: Forecasts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                forecast_value REAL NOT NULL,
                actual_value REAL,
                model_type TEXT,
                scenario_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, model_type, scenario_name)
            )
        """)
        
        # Table 2: Scenarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_name TEXT UNIQUE NOT NULL,
                promo_change REAL,
                oil_change REAL,
                forecast_days INTEGER,
                revenue_impact REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 3: Model Performance
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_type TEXT NOT NULL,
                mape REAL,
                rmse REAL,
                mae REAL,
                r2_score REAL,
                test_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 4: Historical Sales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historical_sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                sales REAL NOT NULL,
                promo_count INTEGER DEFAULT 0,
                oil_price REAL,
                is_holiday INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_forecast(self, date, forecast_value, actual_value=None, model_type="XGBoost", scenario_name="baseline"):
        """
        Save a forecast to the database.
        
        Parameters:
        -----------
        date : str or datetime
            Forecast date
        forecast_value : float
            Forecasted value
        actual_value : float, optional
            Actual value (if known)
        model_type : str
            Type of model used
        scenario_name : str
            Name of scenario
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        date_str = date if isinstance(date, str) else date.strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT OR REPLACE INTO forecasts 
            (date, forecast_value, actual_value, model_type, scenario_name)
            VALUES (?, ?, ?, ?, ?)
        """, (date_str, forecast_value, actual_value, model_type, scenario_name))
        
        conn.commit()
        conn.close()
    
    def save_bulk_forecasts(self, forecast_df, model_type="XGBoost", scenario_name="baseline"):
        """
        Save multiple forecasts at once.
        
        Parameters:
        -----------
        forecast_df : pd.DataFrame
            DataFrame with 'date' and 'forecast' columns
        model_type : str
            Type of model used
        scenario_name : str
            Name of scenario
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for _, row in forecast_df.iterrows():
            date = row['date'] if 'date' in row else row.name
            date_str = date if isinstance(date, str) else pd.to_datetime(date).strftime('%Y-%m-%d')
            forecast_val = row['forecast'] if 'forecast' in row else row.iloc[0]
            actual_val = row.get('actual', None)
            
            cursor.execute("""
                INSERT OR REPLACE INTO forecasts 
                (date, forecast_value, actual_value, model_type, scenario_name)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, forecast_val, actual_val, model_type, scenario_name))
        
        conn.commit()
        conn.close()
    
    def save_scenario(self, scenario_name, promo_change, oil_change, forecast_days, revenue_impact):
        """
        Save scenario parameters.
        
        Parameters:
        -----------
        scenario_name : str
            Name of scenario
        promo_change : float
            Promotion change percentage
        oil_change : float
            Oil price change percentage
        forecast_days : int
            Forecast horizon
        revenue_impact : float
            Calculated revenue impact
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO scenarios 
            (scenario_name, promo_change, oil_change, forecast_days, revenue_impact)
            VALUES (?, ?, ?, ?, ?)
        """, (scenario_name, promo_change, oil_change, forecast_days, revenue_impact))
        
        conn.commit()
        conn.close()
    
    def save_model_performance(self, model_type, mape, rmse, mae, r2_score, test_date=None):
        """
        Save model performance metrics.
        
        Parameters:
        -----------
        model_type : str
            Type of model
        mape : float
            MAPE metric
        rmse : float
            RMSE metric
        mae : float
            MAE metric
        r2_score : float
            R² score
        test_date : str, optional
            Test date
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO model_performance 
            (model_type, mape, rmse, mae, r2_score, test_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (model_type, mape, rmse, mae, r2_score, test_date or datetime.now().strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
    
    def get_forecasts(self, scenario_name=None, model_type=None, start_date=None, end_date=None):
        """
        Retrieve forecasts from database.
        
        Parameters:
        -----------
        scenario_name : str, optional
            Filter by scenario name
        model_type : str, optional
            Filter by model type
        start_date : str, optional
            Start date filter
        end_date : str, optional
            End date filter
            
        Returns:
        --------
        pd.DataFrame : Forecast data
        """
        query = "SELECT * FROM forecasts WHERE 1=1"
        params = []
        
        if scenario_name:
            query += " AND scenario_name = ?"
            params.append(scenario_name)
        
        if model_type:
            query += " AND model_type = ?"
            params.append(model_type)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date"
        
        conn = self._get_connection()
        result = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return result
    
    def get_scenarios(self):
        """Get all saved scenarios."""
        conn = self._get_connection()
        result = pd.read_sql_query("SELECT * FROM scenarios ORDER BY created_at DESC", conn)
        conn.close()
        return result
    
    def get_model_performance_history(self, model_type=None):
        """Get model performance history."""
        conn = self._get_connection()
        query = "SELECT * FROM model_performance"
        if model_type:
            query += " WHERE model_type = ?"
            result = pd.read_sql_query(query, conn, params=[model_type])
        else:
            result = pd.read_sql_query(query, conn)
        conn.close()
        return result
    
    def save_historical_sales(self, df):
        """
        Save historical sales data to database.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with sales data
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for date, row in df.iterrows():
            date_str = date if isinstance(date, str) else pd.to_datetime(date).strftime('%Y-%m-%d')
            sales = row['sales'] if 'sales' in row else row.iloc[0]
            promo_count = row.get('promo_count', 0)
            oil_price = row.get('oil_price', None)
            is_holiday = row.get('is_holiday', 0)
            
            cursor.execute("""
                INSERT OR REPLACE INTO historical_sales 
                (date, sales, promo_count, oil_price, is_holiday)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, sales, promo_count, oil_price, is_holiday))
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """
        Execute a custom SQL query.
        
        Parameters:
        -----------
        query : str
            SQL query
        params : tuple, optional
            Query parameters
            
        Returns:
        --------
        pd.DataFrame : Query results
        """
        conn = self._get_connection()
        result = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return result
    
    def close(self):
        """Close database connection. No-op since connections are created per-operation."""
        pass
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

