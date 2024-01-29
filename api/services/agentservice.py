import json
import requests
from asgiref.sync import async_to_sync
from rest_framework.response import Response
from datetime import datetime
from api.models import User
from api.services.vaultservice import VaultManager
from django.conf import settings
import time


ISSUER_URL = settings.ISSUER_URL
HOLDER_URL = settings.HOLDER_URL
VERIFIER_URL = settings.VERIFIER_URL
ISSUER_API_KEY = settings.ISSUER_API_KEY
HOLDER_API_KEY = settings.HOLDER_API_KEY
VERIFIER_API_KEY = settings.VERIFIER_API_KEY

def createConnection(userId, agent):

    did = User.get_did_by_userId(userId)
    mspId = User.get_mspId_by_did(did)
    jwt_token = VaultManager.retrieve_user_token(did, mspId)
    label = str(User.get_label_by_did(did))

    URL = getAgentUrl(agent)
    ADMIN_API_KEY = getAgentApiKey(agent)

    # 1. Create an invitation from the issuer/verifier agent
    print(f'\n 1. {agent} sends invitation \n')
    invitation_response = requests.post(
        f"{URL}/connections/create-invitation",
        json={
            "label": label,
            "alias": label,
            "auto_accept": True
        },
        headers={
            "x-api-key": ADMIN_API_KEY
        }
    )
    invitation_url = invitation_response.json()["invitation_url"]
    print('invitation_url is ', invitation_url)
    invitation = invitation_response.json()["invitation"]
    print('``````````````````````````````````````')
    print('invitation is ', invitation)

    print('\n 2. Holder receives invitation\n')
    # 2. Connect the holder agent to the issuer agent using the invitation
    connection_response = requests.post(
        f"{HOLDER_URL}/connections/receive-invitation",
        json={
            "@id": invitation['@id'],
            "@type": invitation['@type'],
            "label": invitation['label'],
            "recipientKeys": invitation['recipientKeys'],
            "serviceEndpoint": invitation['serviceEndpoint']
        },
        headers={
            "x-api-key": HOLDER_API_KEY,
            "Authorization": f'Bearer {jwt_token}'
        }
    )
    print('connection_response is: ')
    print(connection_response.json())

    print('\n 3. Holder accepts + stores invitation\n')
    # 3. Holder accepts and stores connection in their wallet

    conn_id = connection_response.json()['connection_id']
    print('conn id is : ', conn_id)
    persistHolderConn(agent, conn_id, did)

    response = requests.post(
        f"{HOLDER_URL}/connections/{conn_id}/accept-invitation",
        headers={
            "x-api-key": HOLDER_API_KEY,
            "Authorization": f'Bearer {jwt_token}'
        }
    )
    print('accept_connection_response is: ')
    print(response.json())
    return response


# webhook function for issuer to accept connection request
def issuer_conn_accept(request, topic, agent):
    print(f'\n Received Connection from {agent} .... \n')
    print('request is ', request.data)
    payload = request.data
    connection_id = payload.get('connection_id', None)

    if connection_id:
        print(f"Topic: {topic}, Connection Id: {connection_id}")
        print('\033[91m'+'topic: ' + '\033[92m', topic)
        print('\033[91m'+'connection_id: ' + '\033[92m', connection_id)

        URL = getAgentUrl(agent)
        print('\033[91m'+'URL: ' + '\033[92m', URL)
        ADMIN_API_KEY = getAgentApiKey(agent)

        wait_a_bit(30)
      
        response = requests.post(
            f"{URL}/connections/{connection_id}/accept-request", headers={
                "x-api-key": ADMIN_API_KEY
            })
        print(
            '\033[91m'+'response from issuer request acceptance : ' + '\033[92m', response)
    
        print('HEADERS ARE ', request.headers.get("x-wallet-id"))

        label = payload.get("their_label")
        persistAgentConn(agent, connection_id, label)

        return Response({'status': 'success'})
    else:
        return Response({"status": "error", "message": "No Connection Id was found in request"})
    

def getConnectionDetails(jwt_token):
    responseIssuer = requests.get(f'{ISSUER_URL}/connections', headers={
        "x-api-key": ISSUER_API_KEY

    }).json()
    responseHolder = requests.get(f'{HOLDER_URL}/connections', headers={
        "x-api-key": HOLDER_API_KEY,
        "Authorization": f'Bearer {jwt_token}'
    }).json()

    active_conn = {}

    responseIssuer = sorted(responseIssuer.get("results"), key=lambda x: datetime.strptime(
        x["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"), reverse=True)
    responseHolder = sorted(responseHolder.get("results"), key=lambda x: datetime.strptime(
        x["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"), reverse=True)

    if responseIssuer:
        for issuer_conn in responseIssuer:
            if issuer_conn["state"] == "active":
                active_conn["issuer_to_holder_conn"] = issuer_conn["connection_id"]
                print('found active connections!')
                break

    if responseHolder:
        for holder_conn in responseHolder:
            if holder_conn["state"] == "active":
                active_conn["holder_to_issuer_conn"] = holder_conn["connection_id"]
                break

    return active_conn


def fetchConnectionDetails(did):
    return User.get_connections_by_did(did)

def getAgentUrl(agent):
    return ISSUER_URL if agent == "issuer" else VERIFIER_URL
def getAgentApiKey(agent):
    return ISSUER_API_KEY if agent == "issuer" else VERIFIER_API_KEY

def persistAgentConn(agent, connection_id, label):
    if agent == "issuer":
        User.update_issuer_connection(issuer_to_holder_conn=connection_id, label=label)
    else:      
        User.update_verifier_holder_connection(verifier_to_holder_conn=connection_id, label=label)

def persistHolderConn(agent, conn_id, did):
    print(f'agent is: {agent}')
    if agent == "issuer":
        User.update_holder_connection(holder_to_issuer_conn=conn_id, did=did)
    else:      
        User.update_holder_verifier_connection(holder_to_verifier_conn=conn_id, did=did)

def wait_a_bit(secs: int = 1):
    total = secs
    print(f"... wait {total} seconds ...")
    time.sleep(total)