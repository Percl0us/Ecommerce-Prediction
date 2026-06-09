# E-Commerce Price Prediction - Quick Start Guide

## ⚡ 5-Minute Quick Start

### 1. Setup
```bash
cd ecommerce-price-prediction
pip install -r requirements.txt
```

### 2. Generate Data
```bash
python src/generate_data.py
```

### 3. Train Model
```bash
python src/train_model.py
```

### 4. Run Web App
```bash
cd deployment
streamlit run app.py
```

### 5. Open in Browser
Visit: `http://localhost:8501`

---

## 📊 Expected Output After Training

```
Test Set Performance:
  MAE:  ₹3,200-4,500
  RMSE: ₹5,500-7,000
  R²:   0.82-0.88
```

---

## 🎯 Project Files

| File | Purpose |
|------|---------|
| `src/generate_data.py` | Creates synthetic dataset |
| `src/build_features.py` | Feature engineering |
| `src/train_model.py` | Model training |
| `src/predict.py` | Making predictions |
| `deployment/app.py` | Streamlit web app |
| `models/` | Saved pipeline (after training) |

---

## 🚀 Next Steps

1. ✅ Train locally
2. 🎨 Customize web app colors/branding
3. 📤 Deploy to Hugging Face Spaces
4. 📊 Add more features or try different models
5. 💡 Experiment with real Kaggle data

---

For full documentation, see **README.md**
