#!/bin/bash

# Variables
REGION="us-west-2"
KEY_PAIR_NAME="indy_key"
KEY_PAIR_PATH="/path/to/key/key.pem"
INSTANCE_TYPE="t2.medium"
AMI_ID="ami-088b024fca114855d" # Ubuntu 20.04 LTS

# Create a VPC
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --region $REGION --query 'Vpc.VpcId' --output text)

# Create subnets
SUBNET_ID_A=$(aws ec2 create-subnet --cidr-block 10.0.1.0/24 --availability-zone ${REGION}a --vpc-id $VPC_ID --query 'Subnet.SubnetId' --output text)
SUBNET_ID_B=$(aws ec2 create-subnet --cidr-block 10.0.2.0/24 --availability-zone ${REGION}b --vpc-id $VPC_ID --query 'Subnet.SubnetId' --output text)

# Create a security group
SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name "validator-node" --description "Validator Node security group" --vpc-id $VPC_ID --query 'GroupId' --output text)

# Add inbound rules to the security group
aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 22 --cidr 0.0.0.0/0

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

# Create four instances
create_instance "ValidatorNode1" $SUBNET_ID_A
create_instance "ValidatorNode2" $SUBNET_ID_A
create_instance "ValidatorNode3" $SUBNET_ID_B
create_instance "ValidatorNode4" $SUBNET_ID_B

# Wait for all instances to be in a running state
echo "Waiting for all instances to be in a running state..."
aws ec2 wait instance-running --instance-ids $(aws ec2 describe-instances --filters "Name=tag:Name,Values=ValidatorNode*" --query 'Reservations[*].Instances[*].InstanceId' --output text)
echo "All instances are now running."

# Note: You will need to SSH into each instance separately and execute the remaining setup steps manually.