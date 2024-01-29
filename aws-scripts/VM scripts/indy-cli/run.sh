#!/bin/bash

echo "SSH into EC2 Instance...."

AWS_KEY_PAIR="stg_key.pem"
EC2_IP="12.34.567.891"

# Copy the setup script to the remote machine
scp -i ~/.ssh/local/"$AWS_KEY_PAIR" indy-cli-setup.sh ubuntu@"$EC2_IP":~

# SSH into the remote machine and execute the copied script
ssh -i ~/.ssh/local/"$AWS_KEY_PAIR" ubuntu@"$EC2_IP" 'bash -s' < ./indy-cli-setup.sh


echo "DONE!"