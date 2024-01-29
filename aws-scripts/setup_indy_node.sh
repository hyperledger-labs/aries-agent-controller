#!/bin/bash

IP_ADDRESS="$1"
KEY_PAIR="/path/to/app/key/key.pem"
LOCAL_PATH="/path/to/app/<APP_NAME>"
REMOTE_PATH="/home/ubuntu/indy-node-container/run/lib_indy/TEST/"
echo "Setup Indy Node: $IP_ADDRESS"

scp -i "${KEY_PAIR}" "ubuntu@$IP_ADDRESS" "git clone --verbose https://github.com/hyperledger/indy-node-container.git"
scp -i "${KEY_PAIR}" "ubuntu@$IP_ADDRESS" "cd indy-node-container/run/ && ./generate_random_seeds.sh"