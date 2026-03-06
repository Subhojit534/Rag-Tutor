# Bedrock Connection Debugging Guide

Your Bedrock health check is returning "disconnected". This guide will help you troubleshoot the connection.

## Quick Diagnostics

### 1. Verify Configuration

Check your `.env` file has these set:

```bash
AWS_REGION=us-east-1
INFERENCE_PROFILE_ARN=arn:aws:bedrock:us-east-1:679626270233:application-inference-profile/9domft7rntuc
AWS_BEARER_TOKEN_BEDROCK=your_actual_bearer_token
```

### 2. Test Bearer Token in Python

```python
python3 << 'EOF'
import os
import json
import boto3
from botocore.config import Config

# Load env variables
from dotenv import load_dotenv
load_dotenv()

bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
region = os.getenv("AWS_REGION", "us-east-1")
profile_arn = os.getenv("INFERENCE_PROFILE_ARN")

print(f"Bearer Token Set: {bool(bearer_token)}")
print(f"Token Length: {len(bearer_token) if bearer_token else 0}")
print(f"Region: {region}")
print(f"Profile ARN: {profile_arn}")

if bearer_token and profile_arn:
    try:
        # Create client with unsigned signature (for bearer token)
        client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(signature_version='UNSIGNED')
        )
        
        # Add bearer token to requests
        def add_bearer_token(request, **kwargs):
            request.headers['Authorization'] = f'Bearer {bearer_token}'
        
        client.meta.events.register('before-send', add_bearer_token)
        
        # Test request
        response = client.invoke_model(
            modelId=profile_arn,
            body=json.dumps({
                "temperature": 0.1,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "test"}]
            })
        )
        
        print("✅ Bedrock connection successful!")
        print(f"Response Status: {response['ResponseMetadata']['HTTPStatusCode']}")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
EOF
```

### 3. Check Bearer Token Validity

- Verify the token is not expired
- Check it's the correct token format (usually starts with `ey...` for JWT-style tokens)
- Confirm the token has permissions for Bedrock

### 4. Verify Application Inference Profile

- Go to AWS Console → Bedrock
- Check "Application Inference Profiles"
- Verify profile exists: `arn:aws:bedrock:us-east-1:679626270233:application-inference-profile/9domft7rntuc`
- Check profile status is "Active"

## Common Issues

### Issue: "UnrecognizedClientException"

**Cause**: Invalid or expired bearer token
**Solution**:

1. Generate a new bearer token from AWS Console
2. Update `AWS_BEARER_TOKEN_BEDROCK` in `.env`
3. Restart the server

### Issue: "ValidationException"  

**Cause**: Invalid Application Inference Profile ARN
**Solution**:

1. Verify ARN format in .env
2. Check profile exists in your AWS account
3. Use correct region

### Issue: "AccessDeniedException"

**Cause**: Bearer token doesn't have Bedrock permissions
**Solution**:

1. Check token permissions in AWS IAM
2. Ensure token has Bedrock access
3. Generate a new token with proper permissions

### Issue: "NoCredentialsError"

**Cause**: Bearer token not being passed correctly
**Solution**:

1. Verify `AWS_BEARER_TOKEN_BEDROCK` is set
2. Check it's not empty
3. Verify server restarted after .env change

## Debugging Steps

### Step 1: Check Environment Variables

```bash
# In backend directory
python3 -c "from app.config import settings; print('Bearer Token:', bool(settings.AWS_BEARER_TOKEN_BEDROCK)); print('Profile ARN:', settings.INFERENCE_PROFILE_ARN); print('Region:', settings.AWS_REGION)"
```

### Step 2: Test Bedrock Client Creation

```bash
python3 -c "
from app.ai.llm import get_bedrock_client
client = get_bedrock_client()
print('Client created:', client is not None)
print('Client type:', type(client).__name__)
"
```

### Step 3: Test Health Check

```bash
python3 -c "
from app.ai.llm import check_bedrock_health
result = check_bedrock_health()
print('Health check result:', result)
"
```

### Step 4: View Server Logs

```bash
# Run the server and see detailed logs
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
# Then in another terminal:
curl -v http://localhost:8000/health
```

## Expected Output

When connected successfully:

```json
{
  "status": "healthy",
  "database": "connected",
  "bedrock": "connected",
  "ai_model": "arn:aws:bedrock:us-east-1:679626270233:application-inference-profile/9domft7rntuc"
}
```

## Next Steps

1. Run the diagnostics above
2. Share any error messages you see
3. Verify all configuration is correct
4. Restart the server after any config changes
5. Check AWS CloudWatch logs for additional errors

---

**Note**: Bearer token authentication with Application Inference Profiles requires:

- Valid, non-expired bearer token
- Unsigned signature version in boto3 config
- Proper Authorization header formatting (`Bearer <token>`)
- Correct Application Inference Profile ARN format
