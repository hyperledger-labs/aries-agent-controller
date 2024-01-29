#!/bin/bash

# Update the package lists for upgrades and new package installations
sudo apt-get update

git clone https://github.com/hyperledger/indy-node-container.git
echo "Cloned Indy-node-container"



# Install necessary python packages
pip3 install -r requirements.txt
echo "DONE! Tool Ready"


