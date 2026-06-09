@echo off
REM E-Commerce Price Prediction - Windows Setup Script
REM This script installs Python dependencies and runs the pipeline

echo.
echo ============================================
echo E-Commerce Price Prediction Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from: https://www.python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/4] Python found:
python --version

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo [3/4] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

REM Run data generation
echo.
echo [4/4] Generating synthetic dataset...
python src\generate_data.py

echo.
echo ============================================
echo ✓ Setup completed!
echo ============================================
echo.
echo Next steps:
echo   1. Activate environment: venv\Scripts\activate
echo   2. Train model: python src\train_model.py
echo   3. Run Streamlit: cd deployment ^&^& streamlit run app.py
echo.
pause
