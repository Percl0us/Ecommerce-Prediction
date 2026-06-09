"""
Feature engineering module for e-commerce price prediction.
Simplified version focusing on numeric and categorical features.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

class FeatureEngineer:
    """Handles feature engineering and preprocessing."""
    
    def __init__(self):
        self.preprocessor = None
        self.feature_names = None
        
    def create_preprocessor(self):
        """Create ColumnTransformer for numeric and categorical features."""
        
        numeric_features = ['discount_percentage', 'rating', 'rating_count']
        categorical_features = ['category']
        
        # Numeric transformer
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        # Categorical transformer
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        self.preprocessor = preprocessor
        return preprocessor
    
    def fit_and_transform(self, df):
        """Fit preprocessor and transform data."""
        df = self._handle_missing_values(df)
        df = self._create_derived_features(df)
        
        X_transformed = self.preprocessor.fit_transform(df)
        self._store_feature_names()
        return X_transformed
    
    def transform(self, df):
        """Transform new data using fitted preprocessor."""
        df = self._handle_missing_values(df)
        df = self._create_derived_features(df)
        return self.preprocessor.transform(df)
    
    @staticmethod
    def _handle_missing_values(df):
        """Handle missing values."""
        df = df.copy()
        
        numeric_cols = ['discount_percentage', 'rating', 'rating_count']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
        
        if 'category' in df.columns:
            df['category'] = df['category'].fillna('Unknown')
        
        return df
    
    @staticmethod
    def _create_derived_features(df):
        """Create derived features."""
        df = df.copy()
        
        if 'actual_price' in df.columns and 'discounted_price' in df.columns:
            df['price_difference'] = df['actual_price'] - df['discounted_price']
        
        if 'rating' in df.columns and 'rating_count' in df.columns:
            df['rating_weight'] = df['rating'] * np.log1p(df['rating_count'])
        
        return df
    
    def _store_feature_names(self):
        """Store feature names from fitted preprocessor."""
        feature_names = []
        
        numeric_features = ['discount_percentage', 'rating', 'rating_count']
        feature_names.extend(numeric_features)
        
        cat_encoder = self.preprocessor.named_transformers_['cat']
        cat_feature_names = cat_encoder.named_steps['onehot'].get_feature_names_out(['category'])
        feature_names.extend(cat_feature_names)
        
        self.feature_names = feature_names
        return feature_names
    
    def save(self, path):
        """Save fitted preprocessor."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.preprocessor, path)
        print(f"✓ Preprocessor saved to {path}")
    
    @staticmethod
    def load(path):
        """Load fitted preprocessor."""
        preprocessor = joblib.load(path)
        engineer = FeatureEngineer()
        engineer.preprocessor = preprocessor
        return engineer
