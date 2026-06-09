# Installation & Setup Guide

## System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space

---

## Step 1: Install Python

### Windows
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"

### macOS
```bash
# Using Homebrew
brew install python3

# Or download from python.org
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

## Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/ecommerce-price-prediction.git
cd ecommerce-price-prediction
```

Or if you don't have Git:
1. Download ZIP from GitHub
2. Extract to desired location
3. Open terminal/cmd in that folder

---

## Step 3: Create Virtual Environment

### Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux (Terminal)
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verification**: You should see `(venv)` in your terminal prompt.

---

## Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- pandas, numpy, scikit-learn
- streamlit, joblib
- faker (for synthetic data)
- boto3 (optional, for AWS)

---

## Step 5: Automated Setup (Optional)

### Windows
```cmd
setup.bat
```

### macOS/Linux
```bash
bash setup.sh
```

These scripts automatically run steps 3-4 above.

---

## Step 6: Generate Data

```bash
python src/generate_data.py
```

**Output:**
```
✓ Dataset created: data/amazon.csv
  Shape: (5000, 8)
```

---

## Step 7: Train Model

```bash
python src/train_model.py
```

**Expected Time**: 2-5 minutes

**Output:**
```
Training model...
Best parameters found:
  model__n_estimators: 100
  model__max_depth: 15

Test Set Performance:
  MAE:  ₹3,456.78
  RMSE: ₹6,234.56
  R²:   0.8567

✓ Pipeline saved to models/price_prediction_pipeline.pkl
✓ Metrics saved to models/training_metrics.json
```

---

## Step 8: Run Streamlit App

```bash
cd deployment
streamlit run app.py
```

**Output:**
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Open in browser**: [http://localhost:8501](http://localhost:8501)

---

## Step 9: Test Predictions

```bash
python src/predict.py
```

**Output:**
```
Making predictions on sample products...

1. Samsung Galaxy Phone
   Category: Electronics
   Actual Price: ₹50,000.00
   Discount: 25.0%
   Predicted Price: ₹37,456.50
```

---

## Troubleshooting

### "Python command not found"
**Windows Solution:**
- Open Control Panel → Apps → Python
- Click → Modify → Add Python to PATH
- Reinstall if needed

**macOS/Linux Solution:**
```bash
# Use python3 instead
python3 -m venv venv
source venv/bin/activate
```

### "ModuleNotFoundError: No module named 'pandas'"
```bash
# Make sure virtual environment is activated
# Then reinstall:
pip install --upgrade pip
pip install -r requirements.txt
```

### "No such file or directory: 'venv\Scripts\activate'"
You're on Linux/Mac, use:
```bash
source venv/bin/activate
```

### Model training fails
```bash
# Check Python version
python --version  # Should be 3.8+

# Check available RAM
# Close other applications
# Try reducing batch size if needed
```

### Streamlit won't start
```bash
# Verify installation
pip show streamlit

# Reinstall
pip install --upgrade streamlit

# Try on different port
streamlit run deployment/app.py --server.port 8502
```

---

## Environment Variables (Optional)

Create `.env` file in project root for AWS credentials:

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

⚠️ Never commit `.env` to GitHub!

---

## Verification Checklist

- [ ] Python installed: `python --version`
- [ ] Virtual env created: `(venv)` appears in prompt
- [ ] Dependencies installed: `pip list | grep pandas`
- [ ] Data generated: `data/amazon.csv` exists (5000+ rows)
- [ ] Model trained: `models/price_prediction_pipeline.pkl` exists
- [ ] Streamlit runs: `http://localhost:8501` accessible
- [ ] Predictions work: `python src/predict.py` outputs prices

---

## Next Steps

✅ **Local Development**
- Modify features in `src/build_features.py`
- Tune hyperparameters in `src/train_model.py`
- Customize app in `deployment/app.py`

📤 **Deploy to Production**
- Follow [DEPLOYMENT.md](DEPLOYMENT.md) for Hugging Face Spaces
- Or [README.md](README.md) for SageMaker setup

📚 **Learn More**
- Read [QUICKSTART.md](QUICKSTART.md) for quick reference
- Check [README.md](README.md) for detailed documentation

---

## Getting Help

- **Errors**: Read full traceback carefully
- **Dependencies**: `pip list` to check installed packages
- **Code**: Check comments in source files
- **Docs**: See README.md for detailed explanations
