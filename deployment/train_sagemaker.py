"""
SageMaker training script for e-commerce price prediction.
Entry point for SageMaker training jobs.

Usage:
    python train_sagemaker.py --data-dir /opt/ml/input/data/training --model-dir /opt/ml/model
"""

import argparse
import json
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

class FeatureEngineer:
    """Feature engineering for training."""
    
    def __init__(self, tfidf_max_features=200):
        self.tfidf_max_features = tfidf_max_features
        self.preprocessor = None
        
    def create_preprocessor(self):
        numeric_features = ['discount_percentage', 'rating', 'rating_count']
        categorical_features = ['category']
        text_features = ['about_product']
        
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        text_transformer = Pipeline(steps=[
            ('tfidf', TfidfVectorizer(max_features=self.tfidf_max_features,
                                     stop_words='english', lowercase=True,
                                     min_df=2, max_df=0.8))
        ])
        
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features),
                ('text', text_transformer, text_features)
            ])
        
        return self.preprocessor
    
    def fit_and_transform(self, df):
        df = df.copy()
        df['discount_percentage'].fillna(df['discount_percentage'].median(), inplace=True)
        df['rating'].fillna(df['rating'].median(), inplace=True)
        df['rating_count'].fillna(df['rating_count'].median(), inplace=True)
        df['category'].fillna(df['category'].mode()[0] if not df['category'].mode().empty else 'Unknown', inplace=True)
        df['about_product'].fillna('', inplace=True)
        
        return self.preprocessor.fit_transform(df)

def main():
    parser = argparse.ArgumentParser()
    
    # SageMaker specific arguments
    parser.add_argument('--data-dir', type=str, default='/opt/ml/input/data/training',
                       help='Path to training data directory')
    parser.add_argument('--model-dir', type=str, default='/opt/ml/model',
                       help='Path to save model')
    parser.add_argument('--output-dir', type=str, default='/opt/ml/output/data',
                       help='Path to output directory')
    
    # Training hyperparameters
    parser.add_argument('--n-estimators', type=int, default=100,
                       help='Number of trees in RandomForest')
    parser.add_argument('--max-depth', type=int, default=15,
                       help='Maximum depth of trees')
    parser.add_argument('--min-samples-split', type=int, default=2,
                       help='Minimum samples required to split')
    
    args, _ = parser.parse_known_args()
    
    # Create output directories
    os.makedirs(args.model_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Training data directory: {args.data_dir}")
    print(f"Model save directory: {args.model_dir}")
    
    # Load training data
    print("Loading training data...")
    train_file = os.path.join(args.data_dir, 'training.csv')
    
    if not os.path.exists(train_file):
        print(f"Error: Training file not found at {train_file}")
        print(f"Available files: {os.listdir(args.data_dir)}")
        raise FileNotFoundError(f"Training file not found at {train_file}")
    
    df = pd.read_csv(train_file)
    print(f"Data shape: {df.shape}")
    
    # Prepare features and target
    X = df.drop('discounted_price', axis=1)
    y = df['discounted_price']
    
    # Train-test split
    print("Splitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Feature engineering
    print("Performing feature engineering...")
    fe = FeatureEngineer(tfidf_max_features=200)
    fe.create_preprocessor()
    X_train_transformed = fe.fit_and_transform(X_train)
    X_test_transformed = fe.preprocessor.transform(X_test)
    
    print(f"Transformed training shape: {X_train_transformed.shape}")
    print(f"Transformed test shape: {X_test_transformed.shape}")
    
    # Build and train model
    print("Training RandomForest model...")
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train_transformed, y_train)
    
    # Evaluate
    print("Evaluating model...")
    y_pred_train = model.predict(X_train_transformed)
    y_pred_test = model.predict(X_test_transformed)
    
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    metrics = {
        'train': {
            'MAE': float(train_mae),
            'RMSE': float(train_rmse),
            'R2': float(train_r2)
        },
        'test': {
            'MAE': float(test_mae),
            'RMSE': float(test_rmse),
            'R2': float(test_r2)
        }
    }
    
    print(f"\nTraining Metrics:")
    print(f"  MAE:  ₹{train_mae:,.2f}")
    print(f"  RMSE: ₹{train_rmse:,.2f}")
    print(f"  R²:   {train_r2:.4f}")
    
    print(f"\nTest Metrics:")
    print(f"  MAE:  ₹{test_mae:,.2f}")
    print(f"  RMSE: ₹{test_rmse:,.2f}")
    print(f"  R²:   {test_r2:.4f}")
    
    # Save model and metrics
    print(f"Saving model to {args.model_dir}...")
    model_path = os.path.join(args.model_dir, 'model.pkl')
    joblib.dump(model, model_path)
    
    # Save metrics
    metrics_path = os.path.join(args.output_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("✓ Training completed successfully!")

if __name__ == '__main__':
    main()
