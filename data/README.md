# Data Directory

## Download Real Dataset (Optional)

To use the real Amazon Sales dataset from Kaggle instead of synthetic data:

1. **Download Dataset**
   - Go to: https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset
   - Download `amazon.csv`
   - Extract and place in this directory

2. **Or Generate Synthetic Data** (Recommended for quick start)
   ```bash
   python ../src/generate_data.py
   ```

## Expected File Structure

```
data/
└── amazon.csv (5,000+ rows with columns:
    - product_name
    - category
    - actual_price
    - discounted_price
    - discount_percentage
    - rating
    - rating_count
    - about_product
)
```

## Notes

- The `amazon.csv` file is gitignored to save space
- Synthetic generation creates realistic data in seconds
- Both real and synthetic data work with the pipeline
