import json
import time
import requests
from rest_framework.response import Response
from api.models import Schema, User
from api.services.vaultservice import VaultManager
from api.services import walletservice
from django.conf import settings


ISSUER_URL = settings.ISSUER_URL
HOLDER_URL = settings.HOLDER_URL
ISSUER_API_KEY = settings.ISSUER_API_KEY
HOLDER_API_KEY = settings.HOLDER_API_KEY
VERIFIER_URL = settings.VERIFIER_URL
VERIFIER_API_KEY = settings.VERIFIER_API_KEY
ISSUER_DID = settings.ISSUER_DID

def send_proof_request(userId, schema_name, version):
    print('Sending proof request... ')

    did = User.get_did_by_userId(userId)
    mspId = User.get_mspId_by_did(did)

    jwt_token = VaultManager.retrieve_user_token(did, mspId)

    connections = User.get_connections_by_did(did)
    verifier_to_holder_connection = connections["verifier_to_holder_conn"]

    schema = Schema.get_schema_by_name_and_version(
        name=schema_name, version=version)
    attributes = schema.attributes

    print("Checking revocation status....")
    resp = check_revocation_status(userId, jwt_token, schema.schema_id)

    if not resp["revoked"]:
        requested_attributes = {}
        for attr_name in attributes:
            requested_attributes[attr_name] = {
                "name": attr_name,
                "restrictions": [{"schema_name": schema_name,  "schema_version": version,
                                "issuer_did": ISSUER_DID}],
            }

        presentation_request = {
            "connection_id": verifier_to_holder_connection,
            "presentation_request": {
                "indy": {
                    "name": "Proof request",
                    # "nonce": "1", #auto-increment
                    "requested_attributes": requested_attributes,
                    "requested_predicates": {},
                    # "non_revoked": {}, #empty = check it was never revoked; can specify timestamp ranges
                    "version": version
                }
            }
        }
        response = requests.post(
            f"{VERIFIER_URL}/present-proof-2.0/send-request", json=presentation_request, headers={
                "Authorization": f'Bearer {jwt_token}',
                "x-api-key": VERIFIER_API_KEY
            })

        print('\033[91m'+'Send proof request to Holder response: ' +
            '\033[92m', response)
        return response.json()
    else:
        return resp

def get_proof(jwt_token):
    response = requests.get(f"{VERIFIER_URL}/present-proof-2.0/records", headers={
        "x-api-key": VERIFIER_API_KEY
    })
    data = json.dumps(response.json())
    data = json.loads(data)
    print('data is ', data)
    return data

def get_credential(userId, jwt_token, schemaId):
    resp = walletservice.fetch_user_cred(userId).json()
    resp = walletservice.filter_by_schema_id(resp, schemaId)
    print("\nresp is \n", resp)
    credential_id = resp["referent"]
    print("\ncredential_id is \n", credential_id)

    response = requests.get(f"{HOLDER_URL}/credential/{credential_id}", headers={
        "Authorization": f'Bearer {jwt_token}'

    })
    data = json.dumps(response.json())
    data = json.loads(data)
    print('data is ', data)
    return data


def handle_presentation_acked(pres_ex_id):

    response = requests.post(
        f"{VERIFIER_URL}/present-proof-2.0/records/{pres_ex_id}/verify-presentation", headers={
            "x-api-key": VERIFIER_API_KEY
        })

    if response.status_code == 200:
        print("Presentation Verification Initiated")
    else:
        print("Error initating presentation verification")


def handle_presentation_verified(payload, pres_ex_id):
    print(f"Presentation verified (pres_ex_id: {pres_ex_id})")
    verified = payload.get("verified")

    if verified:
        print("The proof is sucessfully verified")
    else:
        print("The presentation could not be verified")


def handle_proof_request_received(payload, jwt_token):
    pres_ex_id = payload["pres_ex_id"]
    print("sending request to get present proof record...\n", pres_ex_id)

    response = requests.get(
        f"{HOLDER_URL}/present-proof-2.0/records/{pres_ex_id}", headers={
            "Authorization": f'Bearer {jwt_token}',
            "x-api-key": HOLDER_API_KEY

        })
    if response.status_code == 200:
        request_details = response.json()
        print("result is...\n", request_details)

        presentation_request = request_details.get(
            "by_format", {}).get("pres_request", {})

        presentation = populate_presentation(
            presentation_request, pres_ex_id, jwt_token)
        print("\n presentation  is: \n", presentation)

    response = requests.post(
        f"{HOLDER_URL}/present-proof-2.0/records/{pres_ex_id}/send-presentation", json=presentation, headers={
            "Authorization": f'Bearer {jwt_token}',
            "x-api-key": HOLDER_API_KEY

        })
    print("sending presentation....\n", response.json())
    return response


def handle_presentation_sent(pres_ex_id):
    print(f"Presentation sent (pres_ex_id: {pres_ex_id})")


def populate_presentation(presentation_request, pres_ex_id, jwt_token):
    requested_attributes = presentation_request["indy"]["requested_attributes"]
    requested_predicates = presentation_request["indy"]["requested_predicates"]

    presentation = {
        'self_attested_attributes': {},
        'requested_attributes': {},
        'requested_predicates': {}
    }

 # Retrieve holder's credentials
    response = requests.get(
        f"{HOLDER_URL}/present-proof-2.0/records/{pres_ex_id}/credentials", headers={
            "Authorization": f'Bearer {jwt_token}',
            "x-api-key": HOLDER_API_KEY

        })
    holder_credentials = response.json()
    # get the most recent credential
    holder_credential = holder_credentials[-1]

    presentation = {
        'requested_attributes': {},
        'requested_predicates': {},
        'self_attested_attributes': {},
    }

    for ref_id, req_attr in requested_attributes.items():
        attr_name = req_attr["name"]
        found = False
        for attr, value in holder_credential["cred_info"]["attrs"].items():
            if attr == attr_name:
                found = True
                presentation["requested_attributes"][ref_id] = {
                    "cred_id": holder_credential["cred_info"]["referent"],
                    "revealed": True
                }
                break
        if not found:
            presentation["self_attested_attributes"][ref_id] = "self_attested_value"

    for ref_id, req_pred in requested_predicates.items():
        pred_name = req_pred["name"]
        found = False
        for attr, value in holder_credential["cred_info"]["attrs"].items():
            if attr == pred_name:
                found = True
                presentation["requested_predicates"][ref_id] = {
                    "cred_id": holder_credential["cred_info"]["referent"]
                }
                break
        if not found:
            presentation["self_attested_predicates"][ref_id] = "self_attested_value"

    presentation = {
        'indy':  presentation
    }

    return presentation


def handle_presentation_received(pres_ex_id):
    print(f"Presentation received (pres_ex_id: {pres_ex_id})")

    response = requests.get(
        f"{VERIFIER_URL}/present-proof-2.0/records/{pres_ex_id}", headers={
            "x-api-key": VERIFIER_API_KEY
        })

    if response.status_code == 200:
        presentation_record = response.json()
        # print("Presentation Record is: ", presentation_record)

        presentation_data = presentation_record.get("requested_proof", {})
        print("Presentation data:", presentation_data)

    # Extract and process the requested attributes and predicates
        requested_attributes = presentation_data.get(
            "requested_proof", {}).get("revealed_attrs", {})
        self_attested_attributes = presentation_data.get(
            "requested_proof", {}).get("self_attested_attrs", {})
        requested_predicates = presentation_data.get(
            "requested_proof", {}).get("predicates", {})

        for ref_id, attr_data in requested_attributes.items():
            print(f"Requested attribute ({ref_id}):", attr_data)

        for ref_id, value in self_attested_attributes.items():
            print(f"Self-attested attribute ({ref_id}):", value)

        for ref_id, pred_data in requested_predicates.items():
            print(f"Requested predicate ({ref_id}):", pred_data)

        response = requests.post(
            f"{VERIFIER_URL}/present-proof-2.0/records/{pres_ex_id}/verify-presentation", headers={
                "x-api-key": VERIFIER_API_KEY
            })
        print('verification result state is: ', response.json()["state"])
    else:
        print(
            f"Failed to retrieve presentation record for pres_ex_id {pres_ex_id}")


def check_revocation_status(userId, jwt_token, schema_id):

    resp = walletservice.fetch_user_cred(userId).json()
    resp = walletservice.filter_by_schema_id(resp, schema_id)
    print("\nresp is \n", resp)
    credential_id = resp["referent"]
    print("\ncredential_id is \n", credential_id)

    if resp["rev_reg_id"] == None and resp["cred_rev_id"] == None:
        revoked = False
    else : 
        response = requests.get(
            f"{HOLDER_URL}/credential/revoked/{credential_id}", headers={
                "Authorization": f'Bearer {jwt_token}',
                "x-api-key": HOLDER_API_KEY
            })
        print("revocation status is: ",response.json())
        revoked = response.json()["revoked"]
    resp = {
        "userId":userId,
        "schema_id":schema_id,
        "credential_id":credential_id,
        "revoked": revoked
    }
    return resp