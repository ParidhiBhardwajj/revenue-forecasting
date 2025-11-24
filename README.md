# 📊 Revenue Forecasting Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive business intelligence dashboard for revenue forecasting and scenario analysis, demonstrating advanced data analytics and predictive modeling capabilities.

## 🎯 Project Overview

This project builds an interactive forecasting dashboard that enables business stakeholders to:
- **Predict revenue** using machine learning models (XGBoost, Prophet)
- **Simulate business scenarios** (promotion strategies, oil price changes)
- **Analyze impact** of external factors on revenue
- **Evaluate model performance** with comprehensive metrics
- **Generate reports** with Excel/CSV export functionality
- **Perform statistical analysis** with hypothesis testing and confidence intervals

## ✨ Key Features

### 📈 Interactive Dashboard
- **6 Main Pages**: Overview, Forecasting, Model Analysis, Statistical Analysis, Business Insights, Database
- **Real-time Scenario Simulation**: Adjust promotion levels and oil prices with instant forecast updates
- **Professional Visualizations**: Interactive Plotly charts with custom styling

### 🤖 Machine Learning
- **XGBoost Model**: Gradient boosting for accurate revenue predictions
- **Prophet Model**: Time-series forecasting with seasonality detection
- **Feature Engineering**: 30+ engineered features including lag variables, rolling statistics, and time-based features
- **Model Evaluation**: Comprehensive metrics (MAPE, MAE, RMSE, R²)

### 📊 Business Analytics
- **Scenario Planning**: What-if analysis for business decisions
- **KPI Dashboard**: Revenue impact, ROI calculations, sensitivity analysis
- **Statistical Testing**: T-tests, correlation analysis, confidence intervals
- **Business Metrics**: Year-over-year growth, promotion effectiveness, holiday impact

### 💾 Data Management
- **SQL Database Integration**: SQLite database for storing forecasts, scenarios, and model performance
- **Custom SQL Queries**: Interactive query interface for advanced data retrieval
- **Data Export**: Excel reports with multiple sheets and CSV export functionality

### 📈 Statistical Analysis
- **Hypothesis Testing**: Promotion and holiday impact analysis with p-values
- **Correlation Analysis**: Feature correlations with statistical significance
- **Confidence Intervals**: 95% confidence intervals for forecasts
- **Effect Size Calculations**: Cohen's d for impact quantification

## 🛠️ Technologies & Skills

### Technical Stack
- **Python 3.8+**: Core programming language
- **Streamlit**: Interactive web dashboard framework
- **XGBoost**: Gradient boosting machine learning model
- **Prophet**: Time-series forecasting model
- **Pandas & NumPy**: Data processing and manipulation
- **Plotly**: Interactive data visualization
- **SQLite**: Database management
- **Scikit-learn**: Machine learning utilities
- **Statsmodels**: Statistical analysis
- **OpenPyXL**: Excel file generation

### Skills Demonstrated
- ✅ End-to-end data science pipeline
- ✅ Machine learning model development and evaluation
- ✅ Feature engineering and data preprocessing
- ✅ Statistical analysis and hypothesis testing
- ✅ SQL database design and querying
- ✅ Interactive dashboard development
- ✅ Business analytics and KPI calculation
- ✅ Report generation and data export
- ✅ Scenario planning and what-if analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ParidhiBhardwajj/revenue-forecasting.git
cd revenue-forecasting
```

2. **Add the data file:**
   - The `data/train.csv` file (116MB) is excluded from git due to size limits
   - Place your `train.csv` file in the `data/` directory
   - The other data files (`oil.csv`, `holidays_events.csv`) are included

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the dashboard:**
```bash
streamlit run scripts/app.py
```

Or use the provided script:
```bash
./run.sh
```

4. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
revenue-forecasting/
├── data/                          # Raw data files
│   ├── train.csv                  # Sales data
│   ├── oil.csv                    # Oil price data
│   └── holidays_events.csv        # Holiday calendar
├── scripts/
│   └── app.py                     # Main Streamlit dashboard
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── data_processing.py         # Data loading & feature engineering
│   ├── modeling.py                # ML model training & evaluation
│   ├── visualization.py           # Plotting functions
│   ├── export_functions.py        # Excel/CSV export functionality
│   ├── statistical_analysis.py   # Statistical testing & analysis
│   └── database.py                # SQL database operations
├── requirements.txt               # Python dependencies
├── run.sh                         # Quick start script
├── README.md                      # Project documentation
├── IMPROVEMENTS.md                # Project improvements summary
└── LICENSE                        # MIT License
```

## 📊 Dashboard Pages

### 1. 📈 Overview
- Key metrics and KPIs
- Historical sales trends
- Seasonality patterns
- Dataset summary

### 2. 🔮 Forecasting
- Interactive scenario simulation
- Revenue impact calculations
- Forecast comparison charts
- Excel/CSV export functionality

### 3. 📊 Model Analysis
- Model performance comparison
- Feature importance analysis
- Residual diagnostics
- Evaluation metrics

### 4. 📈 Statistical Analysis
- Hypothesis testing (t-tests)
- Correlation analysis with p-values
- Confidence intervals
- Effect size calculations

### 5. 💼 Business Insights
- Seasonal insights
- Promotion effectiveness
- Holiday impact analysis
- Strategic recommendations

### 6. 💾 Database
- View saved forecasts
- Browse scenarios
- Model performance history
- Custom SQL query interface

## 📈 Key Insights

- **Model Performance**: XGBoost achieves strong predictive accuracy with comprehensive feature engineering
- **Key Drivers**: Oil prices and promotions significantly impact revenue
- **Seasonality**: Strong weekly and monthly patterns identified
- **Statistical Significance**: Promotions and holidays show statistically significant impacts

## 🎓 Business Impact

This dashboard enables data-driven decision making for:
- **Marketing Teams**: Optimize promotion budgets and timing
- **Finance Teams**: Improve revenue forecasting accuracy
- **Executive Leadership**: Strategic planning with scenario modeling
- **Business Analysts**: Comprehensive data analysis and reporting

## 📝 Documentation

- **[Improvements](IMPROVEMENTS.md)**: Summary of project enhancements

## 🔧 Troubleshooting

### Common Issues

**ModuleNotFoundError**: Make sure you're running from the project root directory
```bash
cd revenue-forecasting
streamlit run scripts/app.py
```

**Data not found**: Verify data files are in the `data/` directory

**Port already in use**: Streamlit will automatically use another port, or specify one:
```bash
streamlit run scripts/app.py --server.port 8502
```

For troubleshooting, check the error message and refer to the installation section above.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Paridhi Bhardwaj** - Data Analyst / Business Analyst Portfolio Project

## 🙏 Acknowledgments

- Streamlit for the excellent dashboard framework
- XGBoost and Prophet teams for powerful ML libraries
- The open-source data science community

---

⭐ **Star this repo if you find it helpful!**

*This project demonstrates proficiency in end-to-end data science workflows, from data preparation to deployment of actionable business insights.*
