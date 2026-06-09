"""
Prediction module for e-commerce price prediction.
Loads trained model and makes predictions on new data.
"""

import pandas as pd
import numpy as np
import joblib
import os
from build_features import FeatureEngineer

class PricePredictor:
    """
    Wrapper for making predictions using the trained pipeline.
    """
    
    def __init__(self, model_path='models/price_prediction_pipeline.pkl'):
        self.pipeline = joblib.load(model_path)
        self.model_path = model_path

        if isinstance(self.pipeline, dict):
            self.model = self.pipeline['model']
            self.feature_engineer = self.pipeline['feature_engineer']
        else:
            self.model = self.pipeline
            self.feature_engineer = None

        if hasattr(self.model, 'n_jobs'):
            self.model.n_jobs = 1
    
    def predict_single(self, product_dict):
        """
        Make prediction for a single product.
        
        Args:
            product_dict: Dictionary with keys:
                - product_name (optional, not used in model)
                - category: str
                - actual_price: float
                - discount_percentage: float
                - rating: float
                - rating_count: int
                - about_product: str
        
        Returns:
            Predicted discounted price (float)
        """
        # Create single-row DataFrame
        df = pd.DataFrame([product_dict])
        
        if self.feature_engineer is not None:
            df = self.feature_engineer.transform(df)

        prediction = self.model.predict(df)[0]
        
        return max(0, prediction)  # Ensure non-negative price
    
    def predict_batch(self, df):
        """
        Make predictions for multiple products.
        
        Args:
            df: DataFrame with product features
        
        Returns:
            Array of predictions
        """
        if self.feature_engineer is not None:
            df = self.feature_engineer.transform(df)

        predictions = self.model.predict(df)
        return np.maximum(predictions, 0)  # Ensure non-negative prices
    
    def predict_with_confidence(self, product_dict):
        """
        Make prediction with uncertainty estimate.
        Uses standard deviation of tree predictions as confidence measure.
        
        Args:
            product_dict: Dictionary with product features
        
        Returns:
            Dictionary with prediction and confidence interval
        """
        df = pd.DataFrame([product_dict])
        
        if self.feature_engineer is not None:
            df = self.feature_engineer.transform(df)
            model = self.model
        else:
            model = self.pipeline.named_steps['model']
            df = self.pipeline.named_steps['preprocessor'].transform(df)

        tree_predictions = np.array([tree.predict(df)[0] for tree in model.estimators_])
        
        prediction = np.mean(tree_predictions)
        std_dev = np.std(tree_predictions)
        
        return {
            'prediction': max(0, prediction),
            'lower_bound': max(0, prediction - 1.96 * std_dev),
            'upper_bound': prediction + 1.96 * std_dev,
            'confidence': 1 - (std_dev / prediction) if prediction > 0 else 0
        }

def get_sample_products():
    """
    Return sample products for testing the predictor.
    """
    samples = [
        {
            'product_name': 'Samsung Galaxy Phone',
            'category': 'Electronics',
            'actual_price': 50000.0,
            'discount_percentage': 25.0,
            'rating': 4.5,
            'rating_count': 1500,
            'about_product': 'Latest smartphone with excellent camera and performance'
        },
        {
            'product_name': 'Casual T-Shirt',
            'category': 'Fashion',
            'actual_price': 1500.0,
            'discount_percentage': 40.0,
            'rating': 4.2,
            'rating_count': 300,
            'about_product': 'Cotton t-shirt comfortable for everyday wear'
        },
        {
            'product_name': 'Coffee Maker',
            'category': 'Home & Kitchen',
            'actual_price': 3500.0,
            'discount_percentage': 35.0,
            'rating': 4.0,
            'rating_count': 450,
            'about_product': 'Automatic coffee maker with timer and brew strength control'
        }
    ]
    return samples

if __name__ == '__main__':
    print("Loading trained model...")
    predictor = PricePredictor('models/price_prediction_pipeline.pkl')
    
    print("\nMaking predictions on sample products...\n")
    samples = get_sample_products()
    
    for i, product in enumerate(samples, 1):
        prediction = predictor.predict_single(product)
        print(f"{i}. {product['product_name']}")
        print(f"   Category: {product['category']}")
        print(f"   Actual Price: Rs.{product['actual_price']:,.2f}")
        print(f"   Discount: {product['discount_percentage']:.1f}%")
        print(f"   Predicted Price: Rs.{prediction:,.2f}")
        print()



