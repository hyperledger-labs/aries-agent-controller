 #!/bin/bash 
 # Define the path to your key pair and the username 
 
 KEY_PATH="/path/to/key/key.pem"
 USERNAME="ubuntu" # or ec2-user, depending on your AMI 
 
 # Define the local paths to your genesis files and the remote path where you want to copy them 
 POOL_GENESIS_PATH="/path/to/app/<APP_NAME>/pool_transactions_genesis" 
 DOMAIN_GENESIS_PATH="/path/to/app/<APP_NAME>/domain_transactions_genesis" 
 REMOTE_PATH="/home/ubuntu/indy-node-container/run/lib_indy/<NETWORK_NAME>/"

 # Define the URL of the git repository 
 GIT_REPO_URL="https://github.com/hyperledger/indy-node-container.git" 

 NODE_COUNT=1
 
 # Loop over each IP address in the list 
 while IFS= read -r INSTANCE_IP 
 do 
    echo "Processing instance with IP: $INSTANCE_IP" 
    
     # SSH into the instance and run the commands 
     ssh -i "$KEY_PATH" "$USERNAME"@"$INSTANCE_IP"  
     # Clone the git repository 
     git clone $GIT_REPO_URL 
     cd indy-node-container/run/ 

     # Generate a random seed 
     ./generate_random_seeds.sh 
     
     # Modify the network name 
     sed -i 's/<NETWORK_NAME>/<NETWORK_NAME>/g' etc_indy/indy_config.py 
     sed -i 's/<NETWORK_NAME>/<NETWORK_NAME>/g' .env 
     
     NODE_NAME = "Validator$NODE_COUNT"
     # Modify the node name 
     sed -i "s/Node$NODE_COUNT/$NODE_NAME/g" .env 
    #   sed -i "s/Node1/Validator1/g" .env 

     
     # Prepare the folder for the network 
     rm -rf lib_indy/sovrin_mainnet/ 
     mkdir -p lib_indy/<NETWORK_NAME> 
     
     # Run the setup 
     docker-compose up --scale indy-controller=0 
    
     
     # Copy the genesis files to the instance 
     chmod 400 "$KEY_PATH"
     sudo scp -i "$KEY_PATH" "$POOL_GENESIS_PATH" "$USERNAME"@"$INSTANCE_IP":"$REMOTE_PATH" 
     sudo scp -i "$KEY_PATH" "$DOMAIN_GENESIS_PATH" "$USERNAME"@"$INSTANCE_IP":"$REMOTE_PATH" 

     NODE_COUNT=$((NODE_COUNT+1))

  done < ip_list.txt
