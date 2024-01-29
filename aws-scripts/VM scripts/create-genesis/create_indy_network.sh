#!/bin/bash

NETWORK_NAME="TESTNET"

#Read IP Addr line by line
i=1
while IFS= read -r line
do 

    IP=$(echo $line | cut -d' ' -f1)
    NODE_NAME=$(echo $line | cut -d' ' -f2)
    NODE_ALIAS="Validator$i"

    echo "Setting up Node with IP: $IP." 
    echo "Validator alias: $NODE_ALIAS, Steward name: $NODE_NAME"

    ./install-indy.sh $IP $NODE_ALIAS

    i=$(expr $i + 1)
    
done < ip_tables.sh 