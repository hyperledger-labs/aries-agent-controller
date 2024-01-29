import hvac
import json 
import tempfile
from django.conf import settings

class VaultManager: 

    def init_client():
        client =  hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)

        print(f" Is client authenticated: {client.is_authenticated()}")
        return client

    #===== Vault Store 

    def store_user_seed(did, seed, mspId):
        secret_path = f"/{mspId}/user/{did}/seed"
       
        client = VaultManager.init_client()
        create_response = client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret=dict(seed=seed))
     

    def store_user_token(did, token, mspId):
        secret_path = f"/{mspId}/user/{did}/token"

        client = VaultManager.init_client()
        create_response = client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret=dict(token=token))

    #===== Vault Fetch 

    def retrieve_user_seed(did, mspId):
        secret_path = f"/{mspId}/user/{did}/seed"

        client = VaultManager.init_client()
        response = client.secrets.kv.v2.read_secret_version(path=secret_path)

        return response['data']['data'].get("seed")


    def retrieve_user_token(did, mspId):
        secret_path = f"/{mspId}/user/{did}/token"

        client = VaultManager.init_client()
        response = client.secrets.kv.v2.read_secret_version(path=secret_path)

        return response['data']['data'].get("token")