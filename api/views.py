import json
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.services.vaultservice import VaultManager
from django.conf import settings
from .models import User
import requests

from .serializers import *

from api.services import agentservice
from api.services import issuecredservice
from api.services import verifycredservice
from api.services import walletservice
from api.services import schemaservice
from api.services import revokecredservice


HOLDER_URL = settings.HOLDER_URL
HOLDER_API_KEY = settings.HOLDER_API_KEY

class Register(APIView):

    @swagger_auto_schema(
        request_body=RegisterRequestSerializer,
        responses={200: RegisterResponseSerializer, 500: 'Error'}
    )
    def post(self, request):
        try:
            print('Creating new user identity...')
            print('\n', request, '\n')
            print(request.data)
            
            userId = request.data.get('userId')
            email = request.data.get('email')
            creator = request.data.get('creator')
            mspId = request.data.get('mspId')

            resp = walletservice.create_did(userId, email, creator, mspId)

            return Response(resp, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error: ', e)
            return Response(f'Error: {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('userId', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING, required=True)],
        responses={200: GetUserResponseSerializer}
    )
    def get(self, request):
        userId = request.GET.get('userId', None)
        walletId = User.get_walletId_by_userId(userId)
        response = {}
        if walletId != None:
            response_issuer = requests.get(
                f'{HOLDER_URL}/multitenancy/wallet/{walletId}', headers={
                    "x-api-key": HOLDER_API_KEY
                })
            response = response_issuer.json()
        print(response)
        return Response(response, status=status.HTTP_200_OK)


class Schemas(APIView):
    @swagger_auto_schema(
        request_body=CreateSchemaSerializer,
        responses={200: CreateSchemaResponseSerializer, 500: 'Error'}
    )
    def post(self, request):
        try:
            payload = request.data
            response = schemaservice.create_schema(payload)

            if response:
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print(f'error, {e}')
            return Response(f'error, {e}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses={200: GetSchemaResponseSerializer, 500: 'Error'},
    )
    def get(self, request):
        response = schemaservice.get_existing_schemas()
        return Response(response, status=status.HTTP_200_OK)


class Issue(APIView):
    @swagger_auto_schema(
        request_body=IssueRequestSerializer,
        responses={200: CredentialExchangeSerializer, 500: 'Error'}
    )
    def post(self, request):
        try:
            print('begin issuing credential...')
            payload = request.data
            response = issuecredservice.holderRequestCredentials(payload.get("userId"), payload.get("name"),
                                                                 payload.get("attributes"), payload.get("version"))

            print('Successfully Issued Credential!', response.json())
            return Response(response.json(), status=status.HTTP_200_OK)

        except Exception as e:
            print('error did not send post request \n', e)
            return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        # responses={200: AgentConnectionsResponse, 500: 'Error'},
        manual_parameters=[openapi.Parameter('userId', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING, required=True)],
    ) 
    def get(self, request, format=None):
        userId = request.GET.get('userId', None)
        response = walletservice.fetch_user_cred(userId)
        if response:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_404_NOT_FOUND)


class VerifyUser(APIView):

    @swagger_auto_schema(
        request_body=ProofRequestSerializer,
        responses={200: ProofRequestPostResponseSerializer, 500: 'Error'}
    )
    def post(self, request):
        payload = request.data
        response = verifycredservice.send_proof_request(payload.get(
            "userId"), payload.get("schema_name"), payload.get("version"))
        if response:
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        # responses={200: AgentConnectionsResponse, 500: 'Error'},
        manual_parameters=[openapi.Parameter('userId', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING, required=True)],
    )     
    def get(self, request):
        userId = request.GET.get('userId', None)
        did = User.get_did_by_userId(userId)
        mspId = User.get_mspId_by_did(did)
        response = {}
        if did != None:
            jwt_token = VaultManager.retrieve_user_token(did, mspId)
            response = verifycredservice.get_proof(jwt_token)
            if response:
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response, status=status.HTTP_404_NOT_FOUND)

class Credential(APIView):
     @swagger_auto_schema(
        responses={200: CredentialResponseSerializer, 500: 'Error'},
        manual_parameters=[openapi.Parameter('userId', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('schemaName', openapi.IN_QUERY, description="Schema Name", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('version', openapi.IN_QUERY, description="Version", type=openapi.TYPE_STRING, required=True)],
    )  
     def get(self, request):
        userId = request.GET.get('userId', None)
        schemaName = request.GET.get('schemaName',None)
        version = request.GET.get('version',None)

        schema = Schema.get_schema_by_name_and_version(name=schemaName, version=version)
        schemaId = schema.schema_id
        did = User.get_did_by_userId(userId)
        mspId = User.get_mspId_by_did(did)
        print('schemaId', schemaId)
        response = {}
        
        if did != None:
            jwt_token = VaultManager.retrieve_user_token(did, mspId)
            response = verifycredservice.get_credential(userId, jwt_token, schemaId)
            if response:
                return Response(response['attrs'], status=status.HTTP_200_OK)
            else:
                return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response, status=status.HTTP_404_NOT_FOUND)



class ConnectAgents(APIView):
    @swagger_auto_schema(
        request_body=ConnectAgents,
        responses={200: ConnectionListResponse, 500: 'Error'}
    )
    def post(self, request):
        print('Start Connection .... ')
        userId = request.data.get('userId')

        issuer = agentservice.createConnection(userId, "issuer")
        verifier = agentservice.createConnection(userId, "verifier")
        response = issuer.json(), verifier.json()
        if response:
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses={200: AgentConnectionsResponse, 500: 'Error'},
        manual_parameters=[openapi.Parameter('userId', openapi.IN_QUERY, description="User ID", type=openapi.TYPE_STRING, required=True)],
    ) 
    def get(self, request):
        userId = request.GET.get('userId', None)
        response = {}
        did = User.get_did_by_userId(userId)
        if did != None:
            # jwt_token = VaultManager.retrieve_user_token(did)
            # response = agentservice.getConnectionDetails(jwt_token)
            response = agentservice.fetchConnectionDetails(did)
            if len(response) >= 0:
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(response, status=status.HTTP_404_NOT_FOUND)


class Revoke(APIView):
    def post(self, request):
        cred_def_id = request.data.get('cred_def_id')
        revoc_reg_id = revokecredservice.setupRevocation(
            cred_def_id=cred_def_id)
        if revoc_reg_id:
            print('\nrevoc_reg_id: ', revoc_reg_id, '\n')
            return Response(revoc_reg_id, status=status.HTTP_200_OK)
        else:
            return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        response = revokecredservice.fetch_existing_created_registries()

        if response.json():
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_404_NOT_FOUND)


class RevokeCred(APIView):
    def post(self, request):
        userId = request.data.get('userId')
        schema_name = request.data.get('schema_name')
        version = request.data.get('version')

        response = revokecredservice.revoke_credentials(userId, schema_name, version)
        if response:
            return Response(response.json(), status=status.HTTP_200_OK)
        else:
            return Response('Error', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        # responses={200: AgentConnectionsResponse, 500: 'Error'},
        manual_parameters=[openapi.Parameter('schema_name', openapi.IN_QUERY, description="Schema Name", type=openapi.TYPE_STRING, required=True),
        openapi.Parameter('version', openapi.IN_QUERY, description="Version", type=openapi.TYPE_STRING)],
    ) 
    def get(self, request):
        schema_name = request.GET.get('schema_name')
        version = request.GET.get('version')
        response = revokecredservice.fetch_existing_rev_id(schema_name,version)
        if response:
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(response.json(), status=status.HTTP_404_NOT_FOUND)
