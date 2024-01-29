#!/bin/bash

url='http://localhost:7001'
declare -a agent_names=('issuer' 'verifier' 'holder')

for i in "${!agent_names[@]}"; do
 agent_name=${agent_names[$i]}

 # Generate a new admin API key
 api_key=$(pwgen -s 32 1)
 wallet_key=$(pwgen -s 32 1)
 wallet_seed=$(pwgen -s 32 1)

 echo "Generated new API key for $agent_name: $api_key"

 # Create a wallet for the agent
 wallet_response=$(curl -X POST -H "x-api-key: adminApiKey" -d "{\"method\": \"sov\", \"options\": {\"seed\": \"$wallet_seed\"}}" "$url/wallet/did/create")

 # Extract the DID and verkey from the response
 did=$(echo $wallet_response | jq -r '.result.did')
 verkey=$(echo $wallet_response | jq -r '.result.verkey')

 # Register the agent's DID with the ledger using the steward
 curl -X POST -H "x-api-key: adminApiKey" -d "{\"did\": \"$did\", \"verkey\": \"$verkey\", \"role\": \"ENDORSER\"}" "$url/ledger/register-nym"

 # Give some time for the ledger to process the transaction
 sleep 5

 echo "Registered new agent at $agent_name with DID $did and role ENDORSER."

 # Save the API key, DID, and verkey to AWS Secrets Manager
 aws secretsmanager create-secret --name "$agent_name-api-key" --secret-string "$api_key"
 aws secretsmanager create-secret --name "$agent_name-wallet_key" --secret-string "$wallet_key"
 aws secretsmanager create-secret --name "$agent_name-wallet_seed" --secret-string "$wallet_seed"
 aws secretsmanager create-secret --name "$agent_name-did" --secret-string "$did"
 aws secretsmanager create-secret --name "$agent_name-verkey" --secret-string "$verkey"

 echo "Saved API key, DID, and verkey for $agent_name to AWS Secrets Manager."
done

 echo "Adding additional network monitor did for monitoring"

 api_key=$(pwgen -s 32 1)
 wallet_response=$(curl -X POST -H "x-api-key: adminApiKey" -d "{\"method\": \"sov\", \"options\": {\"seed\": \"$api_key\"}}" "$url/wallet/did/create")
 did=$(echo $wallet_response | jq -r '.result.did')
 verkey=$(echo $wallet_response | jq -r '.result.verkey')
 curl -X POST -H "x-api-key: adminApiKey" -d "{\"did\": \"$did\", \"verkey\": \"$verkey\", \"role\": \"NETWORK_MONITOR\"}" "$url/ledger/register-nym"
 aws secretsmanager create-secret --name "network-monitor-api-key" --secret-string "$api_key"
 aws secretsmanager create-secret --name "network-monitor-did" --secret-string "$did"
 aws secretsmanager create-secret --name "network-monitor-verkey" --secret-string "$verkey"

  echo "Network Monitor did successfully created"
