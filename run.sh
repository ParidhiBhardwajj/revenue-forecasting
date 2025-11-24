#!/bin/bash
# Quick run script for the Revenue Forecasting Dashboard

echo "🚀 Starting Revenue Forecasting Dashboard..."
echo ""

# Check if we're in the right directory
if [ ! -f "scripts/app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Run the dashboard
echo "🎯 Launching dashboard..."
streamlit run scripts/app.py

