#!/bin/bash

# Update the package lists for upgrades and new package installations
sudo apt-get update

# Install Python3 and pip3
sudo apt-get install -y python3 python3-pip

git clone https://github.com/hyperledger/indy-node.git
echo "Cloned Indy-node repo for genesis files"

sudo sh -c 'curl -s https://raw.githubusercontent.com/BorisWilhelms/devcontainer/main/devcontainer.sh > /usr/local/bin/devcontainer && chmod +x /usr/local/bin/devcontainer'


# Install necessary python packages
cd indy-node/.devcontainer
sudo docker build -t indy-node-dev .
echo "Build done, running indy-node-dev container...."

sudo docker run -it indy-node-dev
echo "DONE!"


