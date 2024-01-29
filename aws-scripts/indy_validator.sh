#!/bin/bash

# Replace the following placeholders with your actual values
AWS_KEY_PAIR="<your_aws_key_pair>"
AWS_REGION="us-west-2"
INSTANCE_IDS="<validator_instance_id_1> <validator_instance_id_2> <validator_instance_id_3> <validator_instance_id_4>"
VALIDATOR_ALIAS=("validator1" "validator2" "validator3" "validator4")
NODE_IPS=("<validator_node_ip_1>" "<validator_node_ip_2>" "<validator_node_ip_3>" "<validator_node_ip_4>")
NODE_PORTS=("9701" "9703" "9705" "9707")
CLIENT_IPS=("${NODE_IPS[@]}")
CLIENT_PORTS=("9702" "9704" "9706" "9708")
POOL_GENESIS_URL="<pool_transactions_genesis_url>"
DOMAIN_GENESIS_URL="<domain_transactions_genesis_url>"

# Run the following commands on each of the validator instances
for i in {0..3}; do
    INSTANCE_ID="${INSTANCE_IDS[$i]}"

    # Install required packages and software
    aws ec2-instance-connect send-ssh-public-key --instance-id "$INSTANCE_ID" --availability-zone "$AWS_REGION" --instance-os-user ubuntu --ssh-public-key file://~/.ssh/"$AWS_KEY_PAIR".pub
    ssh -i ~/.ssh/"$AWS_KEY_PAIR" ubuntu@"${NODE_IPS[$i]}" "
        sudo apt update
        sudo apt install -y software-properties-common
        sudo apt-add-repository -y 'deb https://repo.sovrin.org/sdk/deb xenial master'
        sudo apt update
        sudo apt install -y indy-node indy-plenum
        sudo apt install -y indy-cli
    "

    # Configure the node
    ssh -i ~/.ssh/"$AWS_KEY_PAIR" ubuntu@"${NODE_IPS[$i]}" "
        sudo -i -u indy init_indy_node ${VALIDATOR_ALIAS[$i]} ${NODE_IPS[$i]} ${NODE_PORTS[$i]} ${CLIENT_IPS[$i]} ${CLIENT_PORTS[$i]}
        sudo systemctl start indy-node
        sudo systemctl status indy-node.service
        sudo systemctl enable indy-node.service
        sudo validator-info
    "

    # Download the genesis files
    ssh -i ~/.ssh/"$AWS_KEY_PAIR" ubuntu@"${NODE_IPS[$i]}" "
        sudo su - indy
        cd /var/lib/indy/itn
        curl -o domain_transactions_genesis $DOMAIN_GENESIS_URL
        curl -o pool_transactions_genesis $POOL_GENESIS_URL
        exit
    "
done

