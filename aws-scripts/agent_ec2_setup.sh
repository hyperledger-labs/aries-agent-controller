#!/bin/bash
# This script assumes that AWS CLI is installed and configured

# Step 1: Create a new security group
SECURITY_GROUP_NAME="aca-py-sec-group"
SECURITY_GROUP_DESCRIPTION="Security group for ACA-Py agents"
SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name "$SECURITY_GROUP_NAME" --description "$SECURITY_GROUP_DESCRIPTION" --query 'GroupId' --output text)

# Step 2: Create a new EC2 instance
INSTANCE_TYPE="t2.medium"
AMI_ID="ami-088b024fca114855d" # Ubuntu 20.04 LTS # Replace with the appropriate Amazon Linux 2 AMI ID for your region
VOLUME_SIZE=20  # Allocated storage size in GiB
KEY_PAIR_NAME="indy_validator_key"

INSTANCE_ID=$(aws ec2 run-instances --image-id $AMI_ID --count 1 --instance-type $INSTANCE_TYPE --key-name $KEY_PAIR_NAME --security-group-ids $SECURITY_GROUP_ID --block-device-mapping DeviceName=/dev/sda1,Ebs={VolumeSize=$VOLUME_SIZE} --query 'Instances[0].InstanceId' --output text)

# Step 3: Wait for the instance to be in running state
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Step 4: Get the public DNS of the instance
INSTANCE_PUBLIC_DNS=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicDnsName' --output text)

# Output the public DNS
echo "Public DNS of the instance: $INSTANCE_PUBLIC_DNS"