@echo off
echo 🧪 Checking Python version...
python --version || (
    echo ❌ Python not found. Is it installed?
    pause
    exit /b
)

echo ✅ Installing required packages...
pip install streamlit pandas numpy plotly pillow scikit-learn streamlit-extras streamlit-option-menu python-dateutil

echo 🚀 Running Streamlit app...
python -m streamlit run Main.py

echo ⚠️ If nothing opened, check for errors above.
pause
