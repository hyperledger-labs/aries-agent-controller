
#!/bin/bash
docker stop holder
docker rm holder

docker run -p 8001:8001 -p 8002:8002 --name holder --network=bridge -it ghcr.io/hyperledger/aries-cloudagent-python:py3.6-indy-1.16.0-0.8.0 start \
-l  Holder \
-it http 0.0.0.0 8001 \
-ot http \
--admin 0.0.0.0 8002 \
--admin-insecure-mode \
-e http://host.docker.internal:8001 \
--auto-provision \
--genesis-url 'http://host.docker.internal:9000/genesis'  \
--wallet-type askar \
--wallet-name holderwallet \
--trace-target log \
--trace-tag acapy.events \
--wallet-key holderkey \
--seed holder00000000000000000000000000 \
--preserve-exchange-records \
--log-level DEBUG  \
--auto-accept-invites \
--auto-accept-requests \
--auto-ping-connection \
--auto-respond-credential-proposal \
--auto-respond-credential-offer \
--auto-respond-credential-request \
--auto-store-credential \
--public-invites

# aca-py start -l  Holder -it http 0.0.0.0 8000 -ot http --admin 0.0.0.0 8001 --admin-insecure-mode -e http://0.0.0.0:8000/ --genesis-url http://192.168.64.2:9000/genesis  --wallet-type indy --wallet-name holderwallet --wallet-key holderkey --log-level INFO  --auto-provision --auto-accept-invites --auto-accept-requests --auto-ping-connection 

# --webhook-url http://host.docker.internal:8050 \
