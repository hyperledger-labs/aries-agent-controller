#!/bin/bash

git clone https://github.com/hyperledger/indy-node-container.git
cd indy-node-container/run/
./generate_random_seeds.sh 

BUCKET_NAME="testgenesis1"

SECRETS="node_seed"
AWS_REGION="us-west-2"  
NETWORK_NAME="TESTNET"
IP="$1"
NODE_NAME="$2"

CLIENT_PORT=9702
NODE_PORT=9701

source .node.env 
SEED=$(grep 'INDY_NODE_SEED' .node.env | cut -d '=' -f 2)
echo $SEED

# aws secretsmanager update-secret --secret-id "$SECRETS" --secret-string "$seed" --region "$REGION"
aws secretsmanager create-secret --name "$SECRETS" --secret-string "$SEED" --region "$AWS_REGION"

# Change the network name in indy_config.py
sudo sed -i "s/NETWORK_NAME = .*/NETWORK_NAME = '${NETWORK_NAME}'/" etc_indy/indy_config.py

# Change the network name in .env
sudo sed -i "s/INDY_NETWORK_NAME=.*/INDY_NETWORK_NAME=${NETWORK_NAME}/" .env

# Define the new node name and image version
IMAGE_VERSION="ghcr.io/hyperledger/indy-node-container/indy_node:latest-ubuntu20"

# Change the node name in .env
sudo sed -i "s/INDY_NODE_NAME=.*/INDY_NODE_NAME=${NODE_NAME}/" .env
# Change the image version in .env
sudo sed -i "s@IMAGE=.*@IMAGE=${IMAGE_VERSION}@g" .env

sudo rm -rf lib_indy/ssi4de/
sudo mkdir lib_indy/$NETWORK_NAME

#Runs setup to generate info for BLS,POP,Verkey for node
# sudo docker-compose up --scale indy-controller=0 > docker_output.txt

#delete file that contains sensitive data
# sudo rm .node.env

# Extract the values
VERKEY=$(cat docker_output.txt | grep -oP 'Verification key is \K.*')
BLSKEY=$(cat docker_output.txt | grep -oP 'BLS Public key is \K.*')
POP=$(cat docker_output.txt | grep -oP 'Proof of possession for BLS key is \K.*')

# Append values to nodes.csv
echo "Validator$i,$IP,$CLIENT_PORT,$NODE_PORT,$VERKEY,$BLSKEY,$POP" >> nodes$i.csv

# Upload each one to s3
aws s3 cp $NODE_NAME.csv s3://$BUCKET_NAME