  
#!/bin/bash

echo "Retrieving Seeds to populate nodes.csv for genesis... "
# Retrieve the seed from AWS Secrets Manager
SEED=$(aws secretsmanager get-secret-value --secret-id NODE$i --region "$AWS_REGION" | jq -r '.SecretString')