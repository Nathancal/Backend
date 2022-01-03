from functools import wraps
import logging
import azure.functions as httpReqFunc
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
       

        request = httpReqFunc.HttpRequest


        token = request.headers.getter('x-access-token')


        if not token:

            resObj = {"message": "Token is missing"}

            return httpReqFunc.HttpResponse(json.dumps(resObj),status_code=401)
            
     
        secret_name= "token-secret"
        tokenSecret = keyVault.get_secret(secret_name)

        logging.info(tokenSecret.value)

        data = jwt.decode(str(token), tokenSecret.value, algorithms="HS256")

        logging.info(data["user"])

        if data is None: 
            resObj = {"message": "Token is invalid"}

            return httpReqFunc.HttpResponse(json.dumps(resObj), status_code=401)


        return func(*args, **kwargs)

    return jwt_required_wrapper
