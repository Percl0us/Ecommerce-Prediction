# Streamlit Deployment Instructions

## Deploy to Hugging Face Spaces (Free & Easy)

### Step 1: Create Hugging Face Account
- Go to https://huggingface.co
- Sign up for free
- Create an access token in Settings → Access Tokens

### Step 2: Create Space
- Click "New Space"
- Name: `ecommerce-price-prediction`
- License: MIT
- Private: No
- SDK: **Streamlit**
- Create Space

### Step 3: Clone and Setup
```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/ecommerce-price-prediction
cd ecommerce-price-prediction
```

### Step 4: Copy Files
```bash
# From your local project
cp ../deployment/app.py .
cp ../requirements.txt .
mkdir -p models
cp ../models/price_prediction_pipeline.pkl models/
cp ../models/training_metrics.json models/
```

### Step 5: Update Files

**requirements.txt** - Ensure these versions are included:
```
streamlit==1.28.1
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
joblib==1.3.1
```

**app.py** - Verify model loading path is:
```python
model_path = Path(__file__).parent / 'models' / 'price_prediction_pipeline.pkl'
```

### Step 6: Push to Hugging Face
```bash
git add .
git commit -m "Deploy e-commerce price predictor"
git push
```

### Step 7: Wait for Deployment
- Check Space page: https://huggingface.co/spaces/YOUR_USERNAME/ecommerce-price-prediction
- Building should take 3-5 minutes
- Once complete, click "Open in iframe"

### Result
Your live app is now at:
```
https://huggingface.co/spaces/YOUR_USERNAME/ecommerce-price-prediction
```

---

## Troubleshooting Hugging Face Deployment

### App Won't Load
- Check "Logs" in Space settings
- Ensure `streamlit run app.py` is the command
- Verify all imports in app.py are in requirements.txt

### Model Not Found Error
- Confirm model files exist in `models/` directory
- Check file paths in app.py match directory structure

### Memory Error
- Reduce TF-IDF features: `max_features=100` in app.py
- Use smaller batch predictions

### CORS Issues
- Streamlit handles CORS by default
- No additional config needed

---

## Sharing Your Live App

Once deployed, share with anyone:
```
Try my e-commerce price predictor:
https://huggingface.co/spaces/YOUR_USERNAME/ecommerce-price-prediction
```

They can:
1. Enter any product details
2. Get instant price predictions
3. See demo examples
4. View model metrics

No installation required! ✨
