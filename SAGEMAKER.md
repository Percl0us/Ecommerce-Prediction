# AWS SageMaker Deployment Guide

## Prerequisites

- AWS Account (with free tier or paid plan)
- AWS CLI installed: `pip install awscli boto3 sagemaker`
- AWS credentials configured: `aws configure`
- S3 bucket created for storing data and models

---

## Step 1: Set Up AWS Credentials

```bash
# Install AWS tools
pip install awscli boto3 sagemaker

# Configure credentials
aws configure

# Enter:
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1
# Default output: json

# Verify setup
aws sts get-caller-identity
```

---

## Step 2: Create S3 Bucket

```bash
# Create bucket (bucket names must be globally unique)
aws s3 mb s3://my-ecommerce-ml-bucket

# Upload training data
aws s3 cp data/amazon.csv s3://my-ecommerce-ml-bucket/training/amazon.csv

# Verify upload
aws s3 ls s3://my-ecommerce-ml-bucket/training/
```

---

## Step 3: Create SageMaker Notebook Instance

### Via AWS Console
1. Go to AWS SageMaker → Notebook instances
2. Click "Create notebook instance"
3. **Name**: `ecommerce-price-predictor`
4. **Instance type**: `ml.t3.medium` (free tier eligible)
5. **IAM role**: Create new or select existing
6. Click "Create instance" (takes 2-3 minutes)

### Via AWS CLI
```bash
# First, create IAM role if needed
aws iam create-role --role-name SageMakerEcommerceRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "sagemaker.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach policies
aws iam attach-role-policy --role-name SageMakerEcommerceRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy --role-name SageMakerEcommerceRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create notebook instance
aws sagemaker create-notebook-instance \
    --notebook-instance-name ecommerce-price-predictor \
    --instance-type ml.t3.medium \
    --role-arn arn:aws:iam::ACCOUNT_ID:role/SageMakerEcommerceRole
```

---

## Step 4: Set Up Notebook

1. Open notebook instance (click "Open in JupyterLab")
2. Create new notebook: `terminal` → create file `training_job.ipynb`
3. Copy code below into notebook cells:

### Cell 1: Setup
```python
import boto3
import sagemaker
from sagemaker.sklearn.estimator import SKLearn
import pandas as pd

# AWS session
session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()
region = session.boto_region_name

print(f"SageMaker role: {role}")
print(f"S3 bucket: {bucket}")
print(f"Region: {region}")
```

### Cell 2: Upload Training Script
```bash
# In terminal cell, run:
aws s3 cp deployment/train_sagemaker.py s3://my-ecommerce-ml-bucket/code/
```

### Cell 3: Create Training Job
```python
# SKLearn estimator
sklearn_estimator = SKLearn(
    entry_point='train_sagemaker.py',
    source_dir='s3://my-ecommerce-ml-bucket/code/',
    role=role,
    instance_type='ml.m5.xlarge',  # Use ml.m5.large for cost savings
    instance_count=1,
    framework_version='0.23-1',
    py_version='py3',
    script_mode=True,
    hyperparameters={
        'n_estimators': 100,
        'max_depth': 15,
        'min_samples_split': 2
    }
)

# Launch training
training_input = 's3://my-ecommerce-ml-bucket/training/'
sklearn_estimator.fit(training_input)

print(f"Training job name: {sklearn_estimator.latest_training_job.name}")
```

### Cell 4: Deploy Real-Time Endpoint
```python
# Deploy model
predictor = sklearn_estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.t2.medium',
    endpoint_name='ecommerce-price-endpoint'
)

print(f"Endpoint created: ecommerce-price-endpoint")
print(f"Status: {predictor.endpoint_status()}")
```

### Cell 5: Test Predictions
```python
# Sample prediction
test_data = {
    'discount_percentage': [25.0],
    'rating': [4.5],
    'rating_count': [1500],
    'category': ['Electronics'],
    'about_product': ['High quality product']
}

# Format for SageMaker
import json
payload = json.dumps([[0.25, 4.5, 1500, 1, 0, 0, 0, 0, 0, 0, 0, 0, ...]])

# Make prediction
response = predictor.predict(payload)
print(f"Prediction: ₹{response[0]:,.2f}")
```

---

## Step 5: Monitor Training Job

```bash
# Check training status
aws sagemaker describe-training-job \
    --training-job-name ecommerce-price-<timestamp>

# View CloudWatch logs
aws logs tail /aws/sagemaker/NotebookInstances/ecommerce-price-predictor --follow
```

---

## Step 6: Create API Endpoint

### Option A: REST API via SageMaker Endpoint (Automatic)
Your endpoint is already live at:
```
https://ecommerce-price-endpoint.sagemaker.region.amazonaws.com/endpoints/ecommerce-price-endpoint/invocations
```

### Option B: Custom API with API Gateway + Lambda

1. **Create Lambda Function** (Python 3.9)
```python
import boto3
import json

sagemaker_client = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):
    try:
        # Parse input
        body = json.loads(event['body'])
        
        # Format for SageMaker
        payload = json.dumps([
            [
                body['discount_percentage'],
                body['rating'],
                body['rating_count'],
                # ... add categorical and text features
            ]
        ])
        
        # Call SageMaker endpoint
        response = sagemaker_client.invoke_endpoint(
            EndpointName='ecommerce-price-endpoint',
            ContentType='application/json',
            Body=payload
        )
        
        prediction = json.loads(response['Body'].read().decode())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'predicted_price': float(prediction[0])
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

2. **Create API Gateway**
   - Create REST API
   - Create POST resource
   - Connect to Lambda function
   - Deploy to production stage
   - Get API URL

3. **Test API**
```bash
curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{
    "discount_percentage": 25,
    "rating": 4.5,
    "rating_count": 1500
  }'
```

---

## Step 7: Monitor Endpoint

```bash
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name ecommerce-price-endpoint

# View metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/SageMaker \
    --metric-name ModelInvocations \
    --dimensions Name=EndpointName,Value=ecommerce-price-endpoint \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 300 \
    --statistics Sum

# Check endpoint status in console
# SageMaker → Endpoints → ecommerce-price-endpoint
```

---

## Step 8: Clean Up Resources

```bash
# Delete endpoint (stops charges)
aws sagemaker delete-endpoint --endpoint-name ecommerce-price-endpoint

# Delete endpoint configuration
aws sagemaker delete-endpoint-config \
    --endpoint-config-name ecommerce-price-config

# Delete model
aws sagemaker delete-model --model-name ecommerce-price-model

# Delete S3 bucket contents and bucket
aws s3 rm s3://my-ecommerce-ml-bucket --recursive
aws s3 rb s3://my-ecommerce-ml-bucket

# Delete notebook instance
aws sagemaker delete-notebook-instance \
    --notebook-instance-name ecommerce-price-predictor

# Delete IAM role
aws iam detach-role-policy --role-name SageMakerEcommerceRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam delete-role --role-name SageMakerEcommerceRole
```

---

## Cost Estimates

| Resource | Instance Type | Cost/Hour | Notes |
|----------|---|---|---|
| Notebook | ml.t3.medium | $0.0582 | Development only |
| Training | ml.m5.xlarge | $0.269 | Training only |
| Endpoint | ml.t2.medium | $0.0462 | Always running |
| S3 Storage | - | $0.023/GB/month | Minimal |

**Total for 1 month**: ~$33 (endpoint + storage)

💡 Use `ml.m5.large` or `ml.t3.medium` to reduce costs.

---

## Troubleshooting

### "AccessDenied: User is not authorized to perform: sagemaker:..."
- Check IAM role has `AmazonSageMakerFullAccess` policy
- Verify role can access S3 bucket
- Recreate role if needed

### Training job fails
- Check CloudWatch logs: `/aws/sagemaker/TrainingJobs/<job-name>`
- Verify training data in S3 is correctly formatted
- Ensure train_sagemaker.py script is correct

### Endpoint invocation fails
- Verify endpoint is "InService" status
- Check input format matches training data
- Monitor endpoint logs in CloudWatch

### High costs
- Delete unused endpoints immediately
- Use smaller instance types (t2/t3)
- Schedule notebook shutdown when not in use
- Use spot instances for training jobs

---

## Additional Resources

- [SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [SageMaker Python SDK](https://github.com/aws/sagemaker-python-sdk)
- [AWS Free Tier](https://aws.amazon.com/free/) (eligible services)
- [AWS Pricing Calculator](https://calculator.aws/#/)

---

## Next Steps

1. ✅ Deploy notebook and training job
2. ✅ Test endpoint with sample predictions
3. 🔧 Create API Gateway for REST access
4. 📊 Set up CloudWatch monitoring
5. 🚀 Integrate with your application
