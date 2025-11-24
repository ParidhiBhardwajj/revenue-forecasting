# Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard
```bash
streamlit run scripts/app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📁 Project Structure

```
revenue-forecasting/
├── data/                    # Data files (CSV)
├── scripts/
│   └── app.py              # Main dashboard application
├── src/                     # Source code modules
│   ├── __init__.py
│   ├── data_processing.py  # Data loading & feature engineering
│   ├── modeling.py         # ML models & evaluation
│   └── visualization.py    # Chart creation functions
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── IMPROVEMENTS.md        # Summary of enhancements
```

## 🎯 Dashboard Features

### Four Main Pages:

1. **📈 Overview**
   - Key metrics and KPIs
   - Historical sales trends
   - Seasonality patterns
   - Dataset summary

2. **🔮 Forecasting**
   - Interactive scenario simulation
   - Revenue impact calculations
   - Forecast comparison charts
   - Business metrics

3. **📊 Model Analysis**
   - Model performance comparison
   - Feature importance analysis
   - Residual diagnostics
   - Evaluation metrics

4. **💼 Business Insights**
   - Seasonal insights
   - Promotion effectiveness
   - Holiday impact
   - Strategic recommendations

## 💡 Key Features

- **Interactive Controls**: Adjust promotion levels and oil prices in real-time
- **Scenario Planning**: What-if analysis for business decisions
- **Professional Visualizations**: Interactive Plotly charts
- **Comprehensive Metrics**: MAPE, RMSE, R², and business KPIs
- **Business Intelligence**: Automated insights and recommendations

## 🎓 For Resume/Portfolio

### Highlight These Skills:
- ✅ End-to-end data science project
- ✅ Machine learning (XGBoost)
- ✅ Interactive dashboard development
- ✅ Business analytics and KPI calculation
- ✅ Scenario planning and what-if analysis
- ✅ Professional code organization

### Key Metrics to Mention:
- Model accuracy (check the Model Analysis page)
- Number of features engineered
- Business impact metrics calculated

## 🔧 Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Make sure you're running from the project root directory:
```bash
cd /path/to/revenue-forecasting
streamlit run scripts/app.py
```

### Issue: Data not found
**Solution**: Verify your data files are in the `data/` directory:
- `data/train.csv`
- `data/oil.csv`
- `data/holidays_events.csv`

### Issue: Import errors
**Solution**: Install all dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## 📊 Next Steps

1. **Customize**: Adjust model parameters in `src/modeling.py`
2. **Extend**: Add more features in `src/data_processing.py`
3. **Deploy**: Share on Streamlit Cloud
4. **Enhance**: Add more business metrics and insights

---

Happy forecasting! 📈

