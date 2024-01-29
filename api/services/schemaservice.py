import json
import requests
from api.models import Schema
from api.services import revokecredservice
from django.conf import settings

ISSUER_URL = settings.ISSUER_URL
ISSUER_API_KEY = settings.ISSUER_API_KEY

def create_schema(payload):
    data = {
        "attributes": payload.get("attributes"),
        "schema_name": payload.get("schema_name"),
        "schema_version": payload.get("schema_version")
    }

    response = requests.post(f'{ISSUER_URL}/schemas', json=data, headers={
        "x-api-key": ISSUER_API_KEY
    })
    schema = response.json()
    print(response.json())

    print('creating credential definition from schema...')
    credDef = create_cred_def(schema, payload)

    print('cred def is: ', credDef["credential_definition_id"])

    print('\npersisting schema and credential definition...')
    print('payload is: ', payload)

    Schema.save_schema_details(org_name=payload["org_name"], schema_name=data["schema_name"],
                               schema_id=schema["schema_id"], cred_def_id=credDef["credential_definition_id"],
                               attributes=data["attributes"], version=data["schema_version"])

    resp = {
        "schema_id": schema["schema_id"],
        "cred_def_id": credDef["credential_definition_id"]
    }

    return resp


def create_cred_def(schema, payload):
    data = {
        "revocation_registry_size": payload.get("registry_size"),  # 1000
        "schema_id": schema['sent']['schema_id'],
        "support_revocation": payload.get("revocation"),
        "tag": "default"
    }
    response = requests.post(
        f'{ISSUER_URL}/credential-definitions', json=data, headers={
            "x-api-key": ISSUER_API_KEY
        })
    return response.json()


def get_existing_schemas():

    schemas = requests.get(f'{ISSUER_URL}/schemas/created', headers={
        "x-api-key": ISSUER_API_KEY
    })
    credentials = requests.get(f'{ISSUER_URL}/credential-definitions/created', headers={
        "x-api-key": ISSUER_API_KEY
    })
    resp = {
        "schemas": schemas.json(),
        "credential_definitions": credentials.json()
    }
    return resp
