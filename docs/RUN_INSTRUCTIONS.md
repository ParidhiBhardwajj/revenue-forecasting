# How to Run the Revenue Forecasting Dashboard

## 📋 Prerequisites

- Python 3.8 or higher installed on your computer
- pip (Python package manager) - usually comes with Python

## 🚀 Step-by-Step Instructions

### Step 1: Open Terminal/Command Prompt

- **Mac/Linux**: Open Terminal
- **Windows**: Open Command Prompt or PowerShell

### Step 2: Navigate to Project Directory

```bash
cd /Users/paridhibhardwaj/Desktop/revenue-forecasting
```

Or if you're already in the Desktop folder:
```bash
cd revenue-forecasting
```

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

**Note**: If you have multiple Python versions, you might need:
```bash
pip3 install -r requirements.txt
```

Or if you prefer using a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Then install dependencies
pip install -r requirements.txt
```

### Step 4: Run the Dashboard

From the project root directory (`revenue-forecasting/`), run:

```bash
streamlit run scripts/app.py
```

The command will:
1. Start the Streamlit server
2. Automatically open your web browser
3. Display the dashboard at `http://localhost:8501`

### Step 5: Use the Dashboard

- The dashboard will open in your default web browser
- Use the sidebar to navigate between pages and adjust parameters
- Explore the four main sections: Overview, Forecasting, Model Analysis, and Business Insights

## 🔧 Troubleshooting

### Issue: "command not found: streamlit"
**Solution**: Make sure Streamlit is installed:
```bash
pip install streamlit
```

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution**: Make sure you're running the command from the project root directory:
```bash
# Check you're in the right place
pwd  # Should show: /Users/paridhibhardwaj/Desktop/revenue-forecasting

# Then run
streamlit run scripts/app.py
```

### Issue: "FileNotFoundError: data/train.csv"
**Solution**: Verify your data files exist:
```bash
ls data/  # Should show train.csv, oil.csv, holidays_events.csv
```

### Issue: Port already in use
**Solution**: Streamlit will automatically use another port, or specify one:
```bash
streamlit run scripts/app.py --server.port 8502
```

### Issue: Package installation errors
**Solution**: Try upgrading pip first:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

For Prophet specifically (can be tricky):
```bash
# On Mac with conda:
conda install -c conda-forge prophet

# Or install dependencies separately:
pip install pystan
pip install prophet
```

## 📝 Quick Reference

**Full command sequence:**
```bash
# 1. Navigate to project
cd /Users/paridhibhardwaj/Desktop/revenue-forecasting

# 2. Install packages
pip install -r requirements.txt

# 3. Run dashboard
streamlit run scripts/app.py
```

## 🎯 Expected Output

When successful, you should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

The dashboard will automatically open in your browser!

## ⏹️ To Stop the Dashboard

Press `Ctrl + C` in the terminal/command prompt to stop the server.

---

**Need help?** Check the error message and refer to the Troubleshooting section above.

