#!/bin/bash

echo "SSH into EC2 Instance...."

AWS_KEY_PAIR="key.pem"
EC2_IP="12.34.567.891"

echo "Installing indy-cli...."
# # Update the package lists for upgrades and new package installations
# # Ensure CA certificates are installed
sudo apt-get update
sudo apt-get install ca-certificates -y

# # Add the Sovrin repository key
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys CE7709D068DB5E88

# # Add the Sovrin repository
# # Replace "bionic" with "xenial" if you're using Ubuntu 16.04
# # Replace "stable" with "rc" or "master" for different release channels
sudo add-apt-repository "deb https://repo.sovrin.org/sdk/deb bionic stable"

# # Update the package list
sudo apt-get update
# # Install the Indy libraries and CLI
sudo apt-get install -y libindy indy-cli

sudo apt-get update
sudo apt install pwgen

# # Clone the indy-sdk repository
git clone https://github.com/hyperledger/indy-sdk.git

# # Navigate to the indy-sdk/cli directory
cd indy-sdk/cli


sudo apt-get update
sudo apt install cargo 

# # Build the indy-cli
echo "Building Indy Cli...."

cargo build --release

echo "The indy-cli binary can now be found in indy-sdk/cli/target/release/indy"

echo "Generating Trustee info...."

# Add the built indy-cli to PATH for easy access
export PATH=$PATH:$(pwd)/target/release

sudo apt-get update
sudo apt install awscli 

sudo apt-get update
sudo apt install jq 

AWS_REGION="us-west-2"  # replace with your AWS region

# Generate seeds and store them in AWS Secrets Manager
for i in {1..3}
do
    echo "CREATING SEED..."
    SEED=$(pwgen -s 32 1)
    aws secretsmanager create-secret --name "TRUSTEE$i" --secret-string "$SEED" --region "$AWS_REGION"
done

# Create trustees.csv file and add header
echo "TrusteeName,TrusteeDID,TrusteeVerkey" > trustees.csv

# Loop over trustees and create DIDs
for i in 1 2 3
do
  # Retrieve the seed from AWS Secrets Manager
  SEED=$(aws secretsmanager get-secret-value --secret-id TRUSTEE$i --region "$AWS_REGION" | jq -r '.SecretString')
  echo "===trustee$i==="

  # Use echo to pass commands to indy-cli and capture the output
  CLI_OUTPUT=$(echo "wallet open test key=test\ndid new seed=$SEED\nwallet close\nexit\n" | indy-cli)

  echo "CLI output:"
  echo "$CLI_OUTPUT"

  # Extract DID
  DID=$(echo "$CLI_OUTPUT" | grep -oP '(?<=Did ").*(?=" has)')

  # Extract Verkey
  VERKEY=$(echo "$CLI_OUTPUT" | grep -oP '(?<=with ").*(?=" verkey)')

  echo "DID: $DID"
  echo "Verkey: $VERKEY"

  echo "Trustee$i,$DID,$VERKEY" >> trustees.csv
done
