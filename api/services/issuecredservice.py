import requests
import json
from api.models import Schema, User
from api.services.vaultservice import VaultManager
from django.conf import settings

ISSUER_URL = settings.ISSUER_URL
HOLDER_URL = settings.HOLDER_URL
ISSUER_API_KEY = settings.ISSUER_API_KEY
HOLDER_API_KEY = settings.HOLDER_API_KEY
ISSUER_DID = settings.ISSUER_DID
CRED_PREVIEW_TYPE = settings.CRED_PREVIEW_TYPE



def holderRequestCredentials(userId, schema_name, attributes, version):

    cred_preview = {
        "@type": CRED_PREVIEW_TYPE,
        "attributes": [{"name": n, "value": v} for (n, v) in attributes.items()],
    }

    # 0. Fetch user relevant details
    did = User.get_did_by_userId(userId)
    mspId = User.get_mspId_by_did(did)
    jwt_token = VaultManager.retrieve_user_token(did, mspId)

    connections = User.get_connections_by_did(did)
    issuer_to_holder_connection = connections["issuer_to_holder_conn"]

    schema = Schema.get_schema_by_name_and_version(
        name=schema_name, version=version)
    print(schema.schema_id)

   
    # 1. Holder sends proposal
    print('1. Issuer sends offer....')
    response = requests.post(
        f"{ISSUER_URL}/issue-credential-2.0/send-offer",
        json={
            "filter": {
                "indy": {
                    "cred_def_id": schema.cred_def_id,
                    "schema_id": schema.schema_id,
                    "issuer_did": ISSUER_DID,
                }
            },
            "auto_remove": False,
            "comment": "test cred",
            "connection_id": issuer_to_holder_connection,
            "credential_preview": cred_preview,
        },
        headers={
            "x-api-key": ISSUER_API_KEY,
            "Authorization": f'Bearer {jwt_token}'
        }
    )

    return response


def send_credential_offer(cred_ex_id):
    response = requests.post(
        f"{ISSUER_URL}/issue-credential-2.0/records/{cred_ex_id}/send-offer", headers={
            "x-api-key": ISSUER_API_KEY
        })
    if response.status_code == 200:
        print(f"Issued credential for cred_ex_id: ", cred_ex_id)
    else:
        print(f"Failed to issue credential: ", response.text)


def issue_credential(cred_ex_id):
    response = requests.post(
        f"{ISSUER_URL}/issue-credential-2.0/records/{cred_ex_id}/issue", json={}, headers={
            "x-api-key": ISSUER_API_KEY
        })
    if response.status_code == 200:
        print(f"Issued credential for cred_ex_id: ", cred_ex_id)
    else:
        print(f"Failed to issue credential: ", response.text)


def accept_credential_offer(cred_ex_id, jwt_token):
    response = requests.post(
        f"{HOLDER_URL}/issue-credential-2.0/records/{cred_ex_id}/send-request", headers={
            "x-api-key": HOLDER_API_KEY,
            "Authorization": f'Bearer {jwt_token}'
        })
    if response.status_code == 200:
        print(f"Accepted credential for cred_ex_id: ", cred_ex_id)
    else:
        print(f"Failed to accept credential: ", response.text)


def store_credential_offer(cred_ex_id, jwt_token):
    response = requests.post(
        f"{HOLDER_URL}/issue-credential-2.0/records/{cred_ex_id}/store", headers={
            "x-api-key": HOLDER_API_KEY,
            "Authorization": f'Bearer {jwt_token}'
        })
    if response.status_code == 200:
        print(f"Stored credential for cred_ex_id: ", cred_ex_id)
    else:
        print(f"Failed to store credential: ", response.text)
