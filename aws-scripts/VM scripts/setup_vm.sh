#!/bin/bash

# Step 1 - Clone the repo and generate a seed
git clone https://github.com/hyperledger/indy-node-container.git
cd indy-node-container/run/
./generate_random_seeds.sh 

# Extract the seed from the .node.env file
NODE_SEED=$(cat .node.env)
NODE_NAME="NODE_NAME"

# Save it as a secret to AWS Secrets Manager
aws secretsmanager create-secret --name $NODE_NAME --secret-string $NODE_SEED

# Define your network name
NETWORK_NAME="TESTNET"

# Change the network name in indy_config.py
sed -i "s/NETWORK_NAME = .*/NETWORK_NAME = '$NETWORK_NAME'/" etc_indy/indy_config.py

# Update .env file with your network and node name
sed -i "s/INDY_NETWORK_NAME=.*/INDY_NETWORK_NAME=$NETWORK_NAME/" .env
sed -i "s/INDY_NODE_NAME=.*/INDY_NODE_NAME=your_node_alias/" .env

# Prepare the folder
rm -rf lib_indy/ssi4de/
mkdir lib_indy/$NETWORK_NAME

# Run docker-compose to perform setup
docker-compose up --scale indy-controller=0

# Get the keys from the log
VERIFICATION_KEY=$(docker logs indy_node | grep "Verification key is" | awk '{print $5}')
BLS_KEY=$(docker logs indy_node | grep "BLS Public key is" | awk '{print $6}')
PROOF_OF_POSSESSION=$(docker logs indy_node | grep "Proof of possession for BLS key is" | awk '{print $8}')

# Define your node information
STEWARD_NAME=$2
VALIDATOR_ALIAS=$3
NODE_IP_ADDRESS=$1
NODE_PORT=9701
CLIENT_IP_ADDRESS=$1
CLIENT_PORT=9702
STEWARD_DID="your_steward_did"
STEWARD_VERKEY="your_steward_verkey"

# Create the CSV entry
echo "$STEWARD_NAME,$VALIDATOR_ALIAS,$NODE_IP_ADDRESS,$NODE_PORT,$CLIENT_IP_ADDRESS,$CLIENT_PORT,$VERIFICATION_KEY,$BLS_KEY,$PROOF_OF_POSSESSION,$STEWARD_DID,$STEWARD_VERKEY" >> indy_genesis.csv

# Transfer the csv file to another VM
scp indy_genesis.csv username@remote-vm-ip:/path/to/directory

# Run the node
docker-compose up -d