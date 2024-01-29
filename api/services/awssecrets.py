from django.conf import settings
import boto3
import json
from botocore.exceptions import ClientError

def get_secret():
    # Fetch secret name and region from Django settings
    secret_name = settings.SECRET_NAME
    region_name = settings.REGION_NAME

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_string = get_secret_value_response["SecretString"]
        return json.loads(secret_string) 
    except ClientError as e:
        print('Error fetching secret: ', e)
        raise e

