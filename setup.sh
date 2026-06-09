#!/bin/bash
# E-Commerce Price Prediction - Unix/Mac Setup Script

echo "============================================"
echo "E-Commerce Price Prediction Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install from: https://www.python.org"
    exit 1
fi

echo "[1/4] Python found:"
python3 --version

# Create virtual environment
echo ""
echo "[2/4] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo ""
echo "[3/4] Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run data generation
echo ""
echo "[4/4] Generating synthetic dataset..."
python src/generate_data.py

echo ""
echo "============================================"
echo "✓ Setup completed!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Train model: python src/train_model.py"
echo "  3. Run Streamlit: cd deployment && streamlit run app.py"
echo ""
