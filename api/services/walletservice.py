import json
import uuid
import requests
import secrets
from api.services.vaultservice import VaultManager
from api.models import User
from django.conf import settings

ISSUER_URL = settings.ISSUER_URL
HOLDER_URL = settings.HOLDER_URL
ISSUER_API_KEY = settings.ISSUER_API_KEY
HOLDER_API_KEY = settings.HOLDER_API_KEY

def create_did(userId, email, creator, mspId):

    wallet_seed = generate_wallet_key()
    print('wallet_seed generated, creating did...')
    print("MSP ID is: ", mspId)


    data = {
        "method": "sov",
        "options": {
            "key_type": "ed25519"
        },
        "seed": wallet_seed
    }
    print(ISSUER_URL)
    didresponse = requests.post(
        f'{ISSUER_URL}/wallet/did/create', json=data, headers={
            "x-api-key": ISSUER_API_KEY
        })
    userInfo = didresponse.json()['result']
    did = userInfo['did']
    verkey = userInfo['verkey']
    role = "user"
    
    if (creator):
        role = "creator"
        
    print('1. store wallet_seed in vault')
    store_wallet_key(did, wallet_seed, mspId)

    print('2. register did on ledger')
    register_did(did, verkey)
    print('3. create wallet in multitenant agent:')
    label = str(uuid.uuid4())
    walletId, token = create_tenant_wallet(label, wallet_seed)

    print('4. store jwt token in vault:')
    store_token(did, token, mspId)

    print('5. map userId to did + verkey in DB')
    save_user_details(did, userId, verkey, walletId, email, role, label, mspId)

    resp = {
        "did": did,
        "userId": userId,
        "verkey": verkey,
        "email": email,
    }
    print(resp)
    return resp


def create_tenant_wallet(label, wallet_key):
    data = {
        "key_management_mode": "managed",
        "label": label,
        "wallet_dispatch_type": "default",
        "wallet_key": wallet_key,
        "wallet_name": label,
        "wallet_type": "askar",
        "wallet_webhook_urls": [
            "http://host.docker.internal:8000/api/v1/webhooks"
        ]
    }
    print('data is ', data)

    didresponse = requests.post(
        f'{HOLDER_URL}/multitenancy/wallet', json=data,
        headers={
            "x-api-key": HOLDER_API_KEY
        })
    userInfo = didresponse.json()
    walletId = userInfo['wallet_id']
    token = userInfo['token']

    print('multi-tenant wallet info', userInfo)
    return walletId, token


def register_did(did, verkey):
    # post did to ledger publically
    data = {
        "did": did,
        "verkey": verkey
    }
    response = requests.post(
        f'{ISSUER_URL}/ledger/register-nym', json=data, headers={
            "x-api-key": ISSUER_API_KEY
        })
    return response.json()

# Invalidates old token and sets new one


def get_auth_token(walletId):
    response = requests.post(
        f'{HOLDER_URL}/multitenancy/wallet/{walletId}/token', headers={
            "x-api-key": HOLDER_API_KEY,
        })
    return response.json()['token']


def generate_wallet_key():
    return secrets.token_hex(16)


def store_wallet_key(did, wallet_seed, mspId):
    VaultManager.store_user_seed(did, wallet_seed, mspId)
    print('user wallet_key stored')


def store_token(did, token, mspId):
    VaultManager.store_user_token(did, token, mspId)
    print('jwt token stored')


def save_user_details(did, userId, verkey, walletId, email, role, label, mspId):
    User.create_and_save(did=did, userId=userId, verkey=verkey,
                         walletId=walletId, email=email, role=role, label=label, mspId=mspId)
    print('user details saved')


def get_user_credentials(jwt_token):
    response = requests.get(f"{HOLDER_URL}/credentials", headers={
        "Authorization": f'Bearer {jwt_token}',
        "x-api-key": HOLDER_API_KEY

    })
    # response = requests.get(f"{ISSUER_URL}/present-proof-2.0/records")
    data = json.dumps(response.json())
    data = json.loads(data)
    print('data is ', data)
    return data


def fetch_user_cred(userId):
    did = User.get_did_by_userId(userId)
    mspId = User.get_mspId_by_did(did)

    response = {}
    if did != None:
        jwt_token = VaultManager.retrieve_user_token(did, mspId)

        response = requests.get(f'{HOLDER_URL}/credentials', headers={
            "Authorization": f'Bearer {jwt_token}',
            "x-api-key": HOLDER_API_KEY
        })
    return response


def filter_by_schema_id(payload, schema_id):
    print("payload is, ", payload)
    filtered_resp = [item for item in payload["results"] if item['schema_id'] == schema_id]
    print("filtered_resp", filtered_resp)
    

    sorted_resp = sorted(
        filtered_resp, 
        key=lambda cred: int(cred['cred_rev_id']) if cred['cred_rev_id'] and cred['cred_rev_id'] != 'None' else 0,
        reverse=False
    )

    return sorted_resp[-1]
    # return filtered_resp[len(payload["results"])-1] if filtered_resp else None
