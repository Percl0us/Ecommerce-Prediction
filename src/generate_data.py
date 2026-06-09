"""
Data generation script for e-commerce price prediction.
Creates a realistic synthetic Amazon product dataset.
"""

import pandas as pd
import numpy as np
from faker import Faker
import os

np.random.seed(42)
fake = Faker()

def generate_amazon_dataset(n_samples=5000):
    """
    Generate synthetic Amazon-like dataset with realistic distributions.
    
    Columns:
    - product_name: Product name
    - category: Product category (Electronics, Fashion, Home, etc.)
    - actual_price: Original/list price (INR)
    - discounted_price: Selling price (target variable) (INR)
    - discount_percentage: Percentage discount
    - rating: Product rating (1-5)
    - rating_count: Number of ratings
    - about_product: Product description (text)
    """
    
    categories = ['Electronics', 'Fashion', 'Home & Kitchen', 'Books', 
                  'Sports', 'Beauty', 'Toys', 'Furniture']
    
    data = {
        'product_name': [fake.word().title() + ' ' + fake.word().title() for _ in range(n_samples)],
        'category': np.random.choice(categories, n_samples),
        'actual_price': np.random.exponential(scale=3000, size=n_samples) + 500,
        'discount_percentage': np.random.uniform(5, 80, n_samples),
        'rating': np.random.uniform(2, 5, n_samples),
        'rating_count': np.random.exponential(scale=500, size=n_samples).astype(int) + 10,
    }
    
    # Ensure discount_percentage is between 5-80
    data['discount_percentage'] = np.clip(data['discount_percentage'], 5, 80)
    
    # Calculate discounted_price from actual_price and discount_percentage
    data['discounted_price'] = data['actual_price'] * (1 - data['discount_percentage'] / 100)
    
    # Generate product descriptions (about_product)
    product_descriptions = []
    description_templates = [
        "High quality {} with excellent durability. Highly recommended for all age groups.",
        "Premium {} brand ensuring best value for money. Long lasting and reliable.",
        "Best selling {} in its category. Customers love its performance and quality.",
        "Affordable yet {} product perfect for everyday use. Great customer reviews.",
        "Professional grade {} suitable for both beginners and experts. Trusted choice.",
    ]
    
    for _ in range(n_samples):
        template = np.random.choice(description_templates)
        desc = template.format(fake.word())
        product_descriptions.append(desc)
    
    data['about_product'] = product_descriptions
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Round prices to 2 decimals
    df['actual_price'] = df['actual_price'].round(2)
    df['discounted_price'] = df['discounted_price'].round(2)
    df['rating'] = df['rating'].round(2)
    df['discount_percentage'] = df['discount_percentage'].round(2)
    
    # Reorder columns
    df = df[['product_name', 'category', 'actual_price', 'discounted_price', 
             'discount_percentage', 'rating', 'rating_count', 'about_product']]
    
    return df

if __name__ == '__main__':
    print("Generating synthetic Amazon dataset...")
    df = generate_amazon_dataset(5000)
    
    # Save to CSV
    output_path = os.path.join(os.path.dirname(__file__), 'data', 'amazon.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Dataset created: {output_path}")
    print(f"  Shape: {df.shape}")
    print(f"\nFirst few rows:\n{df.head()}")
    print(f"\nDataset statistics:\n{df.describe()}")
