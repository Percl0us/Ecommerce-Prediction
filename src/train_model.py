"""
Model training script for e-commerce price prediction.
Trains RandomForest model on engineered features.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import sys

from build_features import FeatureEngineer

class PricePredictionModel:
    """Manages model training, evaluation, and saving."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.model = None
        self.best_params = None
        
    def build_pipeline(self):
        """Create RandomForest model."""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        return self.model
    
    def train(self, X_train, y_train):
        """Train the model."""
        print("Training model...")
        self.model.fit(X_train, y_train)
        print("✓ Model training completed")
    
    def evaluate(self, X, y, set_name='Test'):
        """Evaluate model on given data."""
        y_pred = self.model.predict(X)
        
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        r2 = r2_score(y, y_pred)
        
        print(f"\n{set_name} Performance:")
        print(f"  R² Score: {r2:.3f}")
        print(f"  MAE (₹): {mae:,.2f}")
        print(f"  RMSE (₹): {rmse:,.2f}")
        
        return {'mae': mae, 'rmse': rmse, 'r2': r2}
    
    def save_pipeline(self, path):
        """Save model and feature engineer."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_engineer': self.feature_engineer
        }, path)
        print(f"\n✓ Model saved to {path}")

def main():
    """Main training pipeline."""
    
    # Load data
    print("Loading data...")
    df = pd.read_csv('src/data/amazon.csv')
    
    # Prepare features
    X = df.drop('discounted_price', axis=1)
    y = df['discounted_price']
    
    print(f"Data shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Train set: {X_train.shape}")
    print(f"Test set:  {X_test.shape}")
    
    # Feature engineering
    print("\nEngineering features...")
    feature_engineer = FeatureEngineer()
    feature_engineer.create_preprocessor()
    
    X_train_transformed = feature_engineer.fit_and_transform(X_train)
    X_test_transformed = feature_engineer.transform(X_test)
    
    print(f"Transformed train shape: {X_train_transformed.shape}")
    print(f"Transformed test shape: {X_test_transformed.shape}")
    
    # Build and train model
    print("\nBuilding model...")
    model = PricePredictionModel()
    model.feature_engineer = feature_engineer
    model.build_pipeline()
    model.train(X_train_transformed, y_train)
    
    # Evaluate
    print("\n" + "="*50)
    model.evaluate(X_train_transformed, y_train, set_name='Train')
    model.evaluate(X_test_transformed, y_test, set_name='Test')
    print("="*50)
    
    # Save
    model.save_pipeline('models/price_prediction_pipeline.pkl')
    print("\n✓ Training complete!")

if __name__ == '__main__':
    main()
