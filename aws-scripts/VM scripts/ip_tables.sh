#!/bin/bash

# Variables
ALLOWLIST=("node_ip_1" "node_ip_2" "controller_ip")  # Add IP addresses of all the nodes in your network and the controller app
NODE_PORT=9701
CLIENT_PORT=9702

# Flush old rules
sudo iptables -F

# Allow incoming and outgoing traffic on the node-to-node port
for ip in "${ALLOWLIST[@]}"; do
   sudo iptables -A INPUT -p tcp -s $ip --dport $NODE_PORT -j ACCEPT
   sudo iptables -A OUTPUT -p tcp -d $ip --sport $NODE_PORT -j ACCEPT
done

# Allow incoming and outgoing traffic on the client-to-node port
for ip in "${ALLOWLIST[@]}"; do
   sudo iptables -A INPUT -p tcp -s $ip --dport $CLIENT_PORT -j ACCEPT
   sudo iptables -A OUTPUT -p tcp -d $ip --sport $CLIENT_PORT -j ACCEPT
done

# Save the rules to be persistent across reboots
sudo netfilter-persistent save