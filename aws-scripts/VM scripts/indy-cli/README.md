# Indy CLI 

In order to generate genesis files for an indy network, we need to create the following files: trustees.csv and nodes.csv. 
These are files that contains certain keys, dids, ports, etc which can be fed into genesis_from_files.py to generate our network genesis files.

Two network genesis files are generated: domain_transaction_genesis, and pool_transaction_genesis. 
Each Node will require a copy of both in order to run and setup the network.

On an initial run of the indy-node, values for the nodes.csv will be generated on each instance.

# Steward tools read me description: 
Use genesis_from_files.py to create genesis files (domain and pool) for a validator
pool. The values of the keys, names, etc. can be completely arbitrary, so this
utility is useful for creating genesis files for actual, rather than test pools
with fixed keys and names.

This script must be run on a system that has the indy-node package installed on it,
for instance, on a validator node.

It requires 2 CSV files as inputs, one containing trustee information for the new
pool, and one containing steward information, including validator node data. The
format of the contents required in the files is as indicated in the output of 
"genesis_from_files.py -h"


# What Indy CLI scripts do 

$ ./run.sh 

This will copy the cli setup script to the single node instance. 
The indy-cli-setup script will install indy-cli and generate the trustees.csv 