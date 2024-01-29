#!/bin/bash
docker stop issuer
docker rm issuer

docker run -p 7000:7000 -p 7001:7001 --name issuer --network=bridge -it ghcr.io/hyperledger/aries-cloudagent-python:py3.6-indy-1.16.0-0.8.0 start \
-l Issuer \
-it http 0.0.0.0 7000 \
-ot http \
--admin 0.0.0.0 7001 \
--admin-insecure-mode \
-e http://host.docker.internal:7000 \
--auto-provision \
--genesis-url 'http://host.docker.internal:9000/genesis'  \
--seed issuer00000000000000000000000000  \
--wallet-type askar \
--trace-target log \
--trace-tag acapy.events \
--wallet-name issuerwallet \
--wallet-key issuerkey \
--log-level DEBUG  \
--preserve-exchange-records \
--auto-accept-invites \
--auto-accept-requests \
--auto-ping-connection \
--auto-respond-credential-proposal \
--auto-respond-credential-offer \
--auto-respond-credential-request \
--auto-store-credential \
--public-invites


# aca-py start -l  Holder -it http 0.0.0.0 7000 -ot http --admin 0.0.0.0 7001 --admin-insecure-mode -e http://0.0.0.0:7000/ --genesis-url http://192.168.64.2:9000/genesis  --wallet-type indy --wallet-name holderwallet --wallet-key holderkey --log-level INFO  --auto-provision --auto-accept-invites --auto-accept-requests --auto-ping-connection --seed issuer00000000000000000000000000  

# --webhook-url http://localhost:8050 \
# --tails-server-base-url http://host.docker.internal:6543
# --auto-respond-presentation-proposal 
# --auto-verify-presentation

#potentially useful examples: 
# PORTS="5001 8001" ./scripts/run_docker start --admin 0.0.0.0 5001 --inbound-transport http 0.0.0.0 8001 --outbound-transport http -e http://host.docker.internal:8001 --admin-insecure-mode --public-invites --auto-ping-connection --auto-accept-invites --auto-accept-requests --auto-respond-presentation-proposal --auto-store-credential --auto-verify-presentation --genesis-url https://indy-test.bosch-digital.de/genesis --seed 00000000000000000000000000000009 --auto-provision --wallet-type askar --wallet-name issuer --wallet-key mykey --wallet-storage-type postgres_storage --wallet-storage-config "{\"url\":\"host.docker.internal:5432\",\"max_connections\":5}" --wallet-storage-creds "{\"account\":\"postgres\",\"password\":\"mysecretpassword\",\"admin_account\":\"postgres\",\"admin_password\":\"mysecretpassword\"}" --tails-server-base-url https://tails.bosch-digital.co --tails-server-upload-url https://tails.bosch-digital.co --notify-revocation --monitor-revocation-notification --emit-new-didcomm-prefix --emit-new-didcomm-mime-type --exch-use-unencrypted-tags
# PORTS="5002 8002" ./scripts/run_docker start --admin 0.0.0.0 5002 --inbound-transport http 0.0.0.0 8002 --outbound-transport http -e http://host.docker.internal:8002 --admin-insecure-mode --public-invites --auto-ping-connection --auto-accept-invites --auto-accept-requests --auto-respond-presentation-proposal --auto-store-credential --auto-verify-presentation --genesis-url https://indy-test.bosch-digital.de/genesis --seed 00000000000000000000000000000007 --auto-provision --wallet-type askar --wallet-name holder --wallet-key mykey --wallet-storage-type postgres_storage --wallet-storage-config "{\"url\":\"host.docker.internal:5432\",\"max_connections\":5}" --wallet-storage-creds "{\"account\":\"postgres\",\"password\":\"mysecretpassword\",\"admin_account\":\"postgres\",\"admin_password\":\"mysecretpassword\"}" --tails-server-base-url https://tails.bosch-digital.co --tails-server-upload-url https://tails.bosch-digital.co --notify-revocation --monitor-revocation-notification --emit-new-didcomm-prefix --emit-new-didcomm-mime-type --exch-use-unencrypted-tags