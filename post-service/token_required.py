from functools import wraps
import azure.functions as functions
import jwt
import json
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
vaultUri = f"https://keyconfig.vault.azure.net"
keyVault = SecretClient(vault_url=vaultUri, credential=credential)


def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):

        request = functions.HttpRequest
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:

            resObj = {"message": "Token is missing"}

            return functions.HttpResponse(json.dumps(resObj),status_code=401)

        try:

            secret_name= "token-secret"
            tokenSecret = keyVault.get_secret(secret_name)

            data = jwt.decode(str(token), tokenSecret, algorithms="HS256")

        except:
            
            resObj = {"message": "Token is invalid"}

            return functions.HttpResponse(resObj, status_code=401)


        return func(*args, **kwargs)

    return jwt_required_wrapper
