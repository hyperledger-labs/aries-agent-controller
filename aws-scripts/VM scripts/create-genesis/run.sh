#!/bin/bash

echo "SSH into EC2 Instance...."

AWS_KEY_PAIR="stg_key.pem"
EC2_IP="12.32.45.789"
SECRETS="node_secrets"
AWS_REGION="us-west-2"


# Copy the setup script to the remote machine
scp -v -i ~/.ssh/local/"$AWS_KEY_PAIR" install-indy.sh ubuntu@"$EC2_IP":~/install-indy.sh

# SSH into the remote machine and execute the copied script
ssh -i ~/.ssh/local/"$AWS_KEY_PAIR" ubuntu@"$EC2_IP" 'bash -s' < ./install-indy.sh


echo "DONE!"