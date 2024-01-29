import json
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import User

from api.services import agentservice
from api.services import issuecredservice
from api.services import verifycredservice
from api.services import revokecredservice
from api.services.vaultservice import VaultManager
from django.conf import settings

HOLDER_URL = settings.HOLDER_URL
HOLDER_API_KEY = settings.HOLDER_API_KEY

# ISSUER WEBHOOK RECEIVER
@api_view(['POST'])
def connections(request, topic, format=None):
    payload = request.data
    state = payload.get("state")
    cred_ex_id = payload.get("cred_ex_id")
    print('\n Received Webhook Request from Issuer .... \n')

    if topic == "connections":
        if state == "request":
            response = agentservice.issuer_conn_accept(request, topic, "issuer")
            if response:
                Response(response, status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif topic == "issue_credential_v2_0":
        if state == "request-received":
            print("\n==ISSUANCE==: request-received\n")
            response = issuecredservice.issue_credential(cred_ex_id)
            if response:
                Response(response.json(), status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif state == "proposal-received":
            print("\n==ISSUANCE==: proposal-receive\n")
            response = issuecredservice.send_credential_offer(cred_ex_id)
            if response:
                Response(response.json(), status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif topic == "present_proof_v2_0":
        state = payload.get("state")
        pres_ex_id = payload.get("pres_ex_id")

        if state == "presentation-received":
            print("\n==PROOF VERIFICATION==: presentation-received\n")
            verifycredservice.handle_presentation_received(pres_ex_id)
        elif state == "presentation-acked":
            print("\n==PROOF VERIFICATION==: presentation_acked\n")
            verifycredservice.handle_presentation_acked(pres_ex_id)
        elif state == "done":
            print("\n==PROOF VERIFICATION==: verified\n")
            verifycredservice.handle_presentation_verified(payload, pres_ex_id)

    elif topic == "revocation_registry":
        state = payload.get("state")

        if state == 'created':
            revokecredservice.handle_registry_created(payload)
            Response(payload, status=status.HTTP_200_OK)
        elif state == 'updated':
            revokecredservice.handle_registry_updated(payload)
            Response(payload, status=status.HTTP_200_OK)

    elif topic == "basicmessages":
        Response(payload, status=status.HTTP_200_OK)

    return Response({'message': 'success'})


# HOLDER WEBHOOK RECEIVER for single holder agent
@api_view(['POST'])
def holder(request, topic, format=None):
    print('\n Received Webhook Request from Holder .... \n')
    payload = request.data
    print('request is ', payload)

    if topic == "issue_credential_v2_0":
        state = payload.get("state")
        cred_ex_id = payload.get("cred_ex_id")

        if state == "proposal-sent":
            print("\n==ISSUANCE==: proposal-sent\n")
            Response(payload, status=status.HTTP_200_OK)

        elif state == "offer-received":
            print("\n==ISSUANCE==: offer-received\n")
            response = issuecredservice.accept_credential_offer(cred_ex_id)
            if response:
                Response(response.json(), status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif state == "credential-received":
            print("\n==ISSUANCE==: credential-received\n")
            response = issuecredservice.store_credential_offer(cred_ex_id)
            if response:
                Response(response.json(), status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif topic == "present_proof_v2_0":
        state = payload.get("state")
        pres_ex_id = payload.get("pres_ex_id")

        if state == "request-received":
            print("\n==PROOF VERIFICATION==: request_received\n")
            verifycredservice.handle_proof_request_received(payload)
        elif state == "presentation-sent":
            print("\n==PROOF VERIFICATION==: presentation_sent\n")
            verifycredservice.handle_presentation_sent(pres_ex_id)

    return Response({'status': 'success'})


# Multitenancy Holder Webhooks
@api_view(['POST'])
def user(request, topic, format=None):
    print('\n Received Webhook Request from User Wallet .... \n')
    payload = request.data

    walletId = request.headers.get('x-wallet-id', None)
    did = User.get_did_by_walletId(walletId)
    mspId = User.get_mspId_by_did(did)

    jwt_token = VaultManager.retrieve_user_token(did, mspId)

    if topic == "connections":
        print("holder wallet connections")
        walletId = request.headers.get("x-wallet-id")
        print('walletId is ', walletId)
        state = payload.get("state")

        connection_id = payload.get("connection_id")

        if state == "response":
            response = requests.post(
                f"{HOLDER_URL}/connections/{connection_id}/send-message", json={"content": "Hello"},
                headers={
                    "Authorization": f'Bearer {jwt_token}',
                    "x-api-key": HOLDER_API_KEY
                })

            Response(response, status=status.HTTP_200_OK)
        else:
            Response(payload, status=status.HTTP_200_OK)

    elif topic == "issue_credential_v2_0":
        state = payload.get("state")
        cred_ex_id = payload.get("cred_ex_id")

        if state == "proposal-sent":
            print("\n==ISSUANCE==: proposal-sent\n")
            Response(payload, status=status.HTTP_200_OK)

        elif state == "offer-received":
            print("\n==ISSUANCE==: offer-received\n")
            response = issuecredservice.accept_credential_offer(
                cred_ex_id, jwt_token)
            if response:
                Response(response.json(), status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif state == "credential-received":
            print("\n==ISSUANCE==: credential-received\n")
            response = issuecredservice.store_credential_offer(
                cred_ex_id, jwt_token)
            if response:
                Response(response.json(), status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif topic == "present_proof_v2_0":
        state = payload.get("state")
        pres_ex_id = payload.get("pres_ex_id")

        if state == "request-received":
            print("\n==PROOF VERIFICATION==: request_received\n")
            verifycredservice.handle_proof_request_received(payload, jwt_token)
        elif state == "presentation-sent":
            print("\n==PROOF VERIFICATION==: presentation_sent\n")
            verifycredservice.handle_presentation_sent(pres_ex_id)

    return Response({'status': 'success'})



@api_view(['POST'])
def proof(request, topic, format=None):
    payload = request.data
    state = payload.get("state")
    cred_ex_id = payload.get("cred_ex_id")
    print('\n Received Webhook Request from Verifier .... \n')
     
    if topic == "connections":
        if state == "request":
            response = agentservice.issuer_conn_accept(request, topic, "verifier")
            if response:
                Response(response, status=status.HTTP_200_OK)
            else:
                Response("Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif topic == "present_proof_v2_0":
        state = payload.get("state")
        pres_ex_id = payload.get("pres_ex_id")

        if state == "presentation-received":
            print("\n==PROOF VERIFICATION==: presentation-received\n")
            verifycredservice.handle_presentation_received(pres_ex_id)
        elif state == "presentation-acked":
            print("\n==PROOF VERIFICATION==: presentation_acked\n")
            verifycredservice.handle_presentation_acked(pres_ex_id)
        elif state == "done":
            print("\n==PROOF VERIFICATION==: verified\n")
            verifycredservice.handle_presentation_verified(payload, pres_ex_id)

    elif topic == "basicmessages":
        Response(payload, status=status.HTTP_200_OK)

    return Response({'message': 'success'})