import requests
import json
from api.models import Schema, User
from api.services.vaultservice import VaultManager
from api.services import walletservice
import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings

ISSUER_URL = settings.ISSUER_URL
ISSUER_API_KEY = settings.ISSUER_API_KEY
CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"


# Flow is for when revocation: false on schema creation. Want to make credential revokable after the fact
def setupRevocation(cred_def_id):
    print("1. Creating revocation registry for cred_def_id: ", cred_def_id)
    rev_reg_id = create_registry(cred_def_id)
    print("2. Updating Tails URI for registry: ", rev_reg_id)
    update_tails_uri(rev_reg_id)
    print("3. Updating registry definition for ledger : ", rev_reg_id)
    create_def(rev_reg_id)
    print("4. Updating tails file to tails-server (s3) : ", rev_reg_id)
    update_tails_ledger(rev_reg_id)
    print("DONE! Credentials are now revokable for: ", cred_def_id)
    return rev_reg_id


def handle_registry_created(payload):
    print("\n ====REVOCATION: registry created \n", payload)


def handle_registry_updated(payload):
    print("\n ====REVOCATION: registry updated \n", payload)


def create_registry(cred_def_id):
    response = requests.post(
        f"{ISSUER_URL}/revocation/create-registry",
        json={
            "credential_definition_id": cred_def_id,
            "max_cred_num": 1000
        },
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )
    response = response.json()["result"]
    print("\nresponse vals, ", response, "\n")

    revoc_reg_id = response["revoc_reg_id"]
    tails_file_path = response["tails_local_path"]
    id = response["id"]
    print("\n", revoc_reg_id, "\n", tails_file_path, "\n", id, "\n")

    return revoc_reg_id


def update_tails_uri(rev_reg_id):
    print('Sending registry definition to the ledger...')

    response = requests.patch(
        f"{ISSUER_URL}/revocation/registry/{rev_reg_id}",
        json={
            "tails_public_uri": f"http://host.docker.internal:6543/{rev_reg_id}"
        },
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )


def create_def(rev_reg_id):
    print('Sending registry definition to the ledger...')

    response = requests.post(
        f"{ISSUER_URL}/revocation/registry/{rev_reg_id}/definition",
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )
    return response.json()["result"]


def update_tails_ledger(rev_reg_id):
    print('Sending registry definition to the ledger...')

    response = requests.put(
        f"{ISSUER_URL}/revocation/registry/{rev_reg_id}/tails-file",
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )
    return response.json()["result"]


def fetch_existing_created_registries():
    response = requests.get(
        f"{ISSUER_URL}/revocation/registries/created",
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )

    return response


def fetch_existing_rev_id(schema_name, version):
    schema = Schema.get_schema_by_name_and_version(schema_name, version)
    cred_def_id = schema.cred_def_id
    print(schema)
    response = requests.get(
        f"{ISSUER_URL}/revocation/active-registry/{cred_def_id}",
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )
    
    return response.json()["result"]


def revoke_credentials(userId, schema_name, version):
    did = User.get_did_by_userId(userId)
    conn = User.get_connections_by_did(did)

    schema = Schema.get_schema_by_name_and_version(name=schema_name, version=version) 

    resp = walletservice.fetch_user_cred(userId).json()
    resp = walletservice.filter_by_schema_id(resp, schema.schema_id)
    print("\n filtered resp: \n", resp)

    payload = {
        "comment": f"revoking credential: {schema_name}",
        "connection_id": conn["issuer_to_holder_conn"],
        "cred_rev_id": resp["cred_rev_id"],
        "notify": "true",
        "notify_version": "v1_0",
        "publish": "true",
        "rev_reg_id": resp["rev_reg_id"],
        "thread_id": "-"
    }

    print('\ncred payload sent to be revoked is \n', payload)

    response = requests.post(
        f"{ISSUER_URL}/revocation/revoke",
        json=payload,
        headers={
            "x-api-key": ISSUER_API_KEY
        }
    )

    print('\nrevocation result is: \n', response.json())
    return response
