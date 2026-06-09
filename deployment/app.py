"""
Streamlit web app for e-commerce price prediction.
Deployed at: https://huggingface.co/spaces/[YOUR_USERNAME]/ecommerce-price-prediction
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="E-Commerce Price Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional and minimal
st.markdown("""
<style>
    .prediction-box {
        background-color: #f5f5f5;
        border-left: 4px solid #333;
        padding: 20px;
        border-radius: 4px;
        margin: 20px 0;
    }
    .prediction-value {
        font-size: 28px;
        font-weight: 600;
        color: #333;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    """Load pre-trained model pipeline."""
    model_path = Path(__file__).parent.parent / 'models' / 'price_prediction_pipeline.pkl'
    
    # For Hugging Face Spaces, model is in the same directory
    if not model_path.exists():
        model_path = Path('../models/price_prediction_pipeline.pkl')
    
    if not model_path.exists():
        st.error(f"Error: Model not found at {model_path}")
        st.stop()
    
    try:
        loaded_data = joblib.load(str(model_path))
        
        # Handle both dict and direct model formats
        if isinstance(loaded_data, dict):
            pipeline = loaded_data['model']
            feature_engineer = loaded_data['feature_engineer']
            return {'model': pipeline, 'feature_engineer': feature_engineer}
        else:
            return loaded_data
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

@st.cache_data
def load_metrics():
    """Load training metrics."""
    metrics_path = Path(__file__).parent / 'models' / 'training_metrics.json'
    
    if not metrics_path.exists():
        metrics_path = Path('./models/training_metrics.json')
    
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return None

def predict_price(pipeline_obj, feature_engineer, product_data):
    """Make prediction using the trained pipeline."""
    try:
        df = pd.DataFrame([product_data])
        X_transformed = feature_engineer.transform(df)
        prediction = pipeline_obj.predict(X_transformed)[0]
        return max(0, prediction)
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return None

# Main app
st.title("E-Commerce Price Predictor")
st.markdown("Predict discounted product prices using machine learning")

# Load model and metrics
pipeline = load_model()
metrics = load_metrics()

# Sidebar
with st.sidebar:
    st.header("Model Information")
    
    if metrics:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MAE", f"₹{metrics['Test']['MAE']:,.0f}")
            st.metric("R² Score", f"{metrics['Test']['R2']:.4f}")
        with col2:
            st.metric("RMSE", f"₹{metrics['Test']['RMSE']:,.0f}")
            st.metric("MAPE", f"{metrics['Test']['MAPE']:.2f}%")
    
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    This model predicts the **discounted price** of e-commerce products based on:
    
    - Product category
    - Original price
    - Discount percentage
    - Customer rating & review count
    - Product description
    
    **Model Type**: Random Forest Regressor with GridSearchCV tuning
    
    **Training Data**: 5,000 e-commerce products
    """)

# Main content
tab1, tab2, tab3 = st.tabs(["Predict", "Demo", "Information"])

with tab1:
    st.subheader("Enter Product Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Category",
            ['Electronics', 'Fashion', 'Home & Kitchen', 'Books', 
             'Sports', 'Beauty', 'Toys', 'Furniture']
        )
        actual_price = st.number_input(
            "Actual Price (₹)",
            min_value=100,
            max_value=500000,
            value=10000,
            step=100
        )
        rating = st.slider(
            "Customer Rating",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.1
        )
    
    with col2:
        discount_percentage = st.slider(
            "Discount (%)",
            min_value=5,
            max_value=80,
            value=25,
            step=1
        )
        rating_count = st.number_input(
            "Number of Ratings",
            min_value=1,
            max_value=100000,
            value=500,
            step=10
        )
    
    about_product = st.text_area(
        "Product Description",
        value="High quality product with excellent performance",
        height=100
    )
    
    # Prediction
    if st.button("Predict Price", use_container_width=True, type="primary"):
        product_data = {
            'product_name': 'User Product',
            'category': category,
            'actual_price': actual_price,
            'discount_percentage': discount_percentage,
            'rating': rating,
            'rating_count': rating_count,
            'about_product': about_product
        }
        
        prediction = predict_price(pipeline['model'], pipeline['feature_engineer'], product_data)
        
        if prediction is not None:
            st.markdown(f"""
            <div class="prediction-box">
                <strong>Predicted Discounted Price</strong>
                <div class="prediction-value">₹{prediction:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show additional metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Original Price", f"₹{actual_price:,.0f}")
            with col2:
                expected_discount = actual_price * discount_percentage / 100
                st.metric("Expected Discount", f"₹{expected_discount:,.0f}")
            with col3:
                actual_discount = actual_price - prediction
                st.metric("Predicted Discount", f"₹{actual_discount:,.0f}")

with tab2:
    st.subheader("Demo Predictions")
    st.markdown("Sample predictions for demonstration:")
    
    demo_products = [
        {
            'name': 'Samsung Galaxy S23',
            'category': 'Electronics',
            'actual_price': 79999,
            'discount_percentage': 20,
            'rating': 4.7,
            'rating_count': 2500,
            'about_product': 'Latest flagship smartphone with excellent camera and processor'
        },
        {
            'name': 'Nike Running Shoes',
            'category': 'Fashion',
            'actual_price': 8500,
            'discount_percentage': 35,
            'rating': 4.4,
            'rating_count': 1200,
            'about_product': 'Lightweight running shoes with excellent cushioning'
        },
        {
            'name': 'KitchenAid Mixer',
            'category': 'Home & Kitchen',
            'actual_price': 35000,
            'discount_percentage': 30,
            'rating': 4.6,
            'rating_count': 800,
            'about_product': 'Professional grade stand mixer perfect for baking'
        }
    ]
    
    for product in demo_products:
        prediction = predict_price(pipeline['model'], pipeline['feature_engineer'], {
            'product_name': product['name'],
            'category': product['category'],
            'actual_price': product['actual_price'],
            'discount_percentage': product['discount_percentage'],
            'rating': product['rating'],
            'rating_count': product['rating_count'],
            'about_product': product['about_product']
        })
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{product['name']}**")
        with col2:
            st.write(f"₹{product['actual_price']:,}")
        with col3:
            st.write(f"{product['discount_percentage']}% off")
        with col4:
            if prediction:
                st.write(f"**₹{prediction:,.0f}**")

with tab3:
    st.subheader("How It Works")
    
    st.markdown("""
    ### Model Architecture
    
    This project uses a Random Forest Regressor with the following pipeline:
    
    **1. Feature Engineering**
    - Numeric features scaled with StandardScaler
    - Categorical features one-hot encoded
    - Text descriptions vectorized with TF-IDF
    - Derived features created for enhanced prediction
    
    **2. Model Training**
    - 80/20 train-test split
    - Hyperparameter tuning with GridSearchCV
    - 5-fold cross-validation
    
    **3. Performance Metrics**
    """)
    
    if metrics:
        metric_df = pd.DataFrame(metrics['Test']).T.reset_index()
        metric_df.columns = ['Metric', 'Value']
        st.dataframe(metric_df, use_container_width=True)
    
    st.markdown("""
    ### Dataset
    - Size: 5,000 products
    - Features: 8 original + 2 derived
    - Categories: Electronics, Fashion, Home & Kitchen, Books, Sports, Beauty, Toys, Furniture
    
    ### Technologies
    - Framework: scikit-learn
    - Deployment: Streamlit
    - Model Storage: joblib
    
    ### Source Code
    [GitHub Repository](https://github.com/yourusername/ecommerce-price-prediction)
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
E-Commerce Price Prediction | 
<a href="https://github.com/yourusername/ecommerce-price-prediction">GitHub Repository</a>
</div>
""", unsafe_allow_html=True)
