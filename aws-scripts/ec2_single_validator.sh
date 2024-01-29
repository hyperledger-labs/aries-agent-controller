#!/bin/bash

# Variables

REGION="us-west-2"
KEY_PAIR_NAME="indy_key"
KEY_PAIR_PATH="/path/to/key/key.pem"
INSTANCE_TYPE="t2.medium"
AMI_ID="ami-088b024fca114855d" # Ubuntu 20.04 LTS
VPC_ID="vpc-1234"
SECURITY_GROUP_ID="sg-1234"
SUBNET_ID_A="subnet-1234"


# Function to create an EC2 instance
create_instance() {
    INSTANCE_NAME=$1
    SUBNET_ID=$2
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_PAIR_NAME \
        --security-group-ids $SECURITY_GROUP_ID \
        --subnet-id $SUBNET_ID \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    echo "Created instance $INSTANCE_NAME with ID $INSTANCE_ID"
}

create_instance "ValidatorNode1" $SUBNET_ID_A

# Allocate an Elastic IP
ELASTIC_IP=$(aws ec2 allocate-address --domain vpc --query 'PublicIp' --output text)

# Associate Elastic IP with the instance
aws ec2 associate-address --instance-id $INSTANCE_ID --public-ip $ELASTIC_IP

# Wait for the instance to be in a running state
echo "Waiting for the instance to be in a running state..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID
echo "Instance is now running."

# SSH into the instance
ssh -i $KEY_PAIR_PATH ubuntu@$ELASTIC_IP

# Execute the remaining setup steps in the instance