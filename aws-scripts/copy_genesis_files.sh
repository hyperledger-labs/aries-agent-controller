#!/bin/bash

IP_ADDRESS="12.234.567.891"
KEY_PAIR="/path/to/key/key.pem"
LOCAL_PATH="/path/APP_NAME/"
REMOTE_PATH="/home/ubuntu/indy-node-container/run/lib_indy/<NETWORK_NAME>/"
echo "Copying genesis files for: $IP_ADDRESS"

echo "pool_transactions_genesis"

scp -v -i "${KEY_PAIR}" "${LOCAL_PATH}pool_transactions_genesis" "ubuntu@${EC2_IP}:${REMOTE_PATH}"
echo "domain_transactions_genesis"

scp -v -i "${KEY_PAIR}" "${LOCAL_PATH}domain_transactions_genesis" "ubuntu@${EC2_IP}:${REMOTE_PATH}"