import logging
import uuid
import jwt
import json
import bcrypt
import datetime
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='

credential = DefaultAzureCredential()
vaultUri = f"https://keyconfig.vault.azure.net"
keyVault = SecretClient(vault_url=vaultUri, credential=credential)
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    user_db = cosmosClient.get_database_client('users')
    user_container = user_db.get_container_client('user')

    email = str(req.form["email"])

    query = "SELECT * FROM users WHERE users.email=@email"


    check_email = list(user_container.query_items(
        query=query,
        parameters=[{
            "name":"@email", "value": email
        }],
        enable_cross_partition_query=True
    ))[0]

    logging.info(check_email)

    if check_email:

        password = str(req.form["password"])
        crossRefPassword = bytes(check_email["password"], encoding='UTF-8')

        if bcrypt.checkpw(bytes(password, 'UTF-8'), crossRefPassword):

            try:
                secret_name= "token-secret"
                tokenSecret = keyVault.get_secret(secret_name)

                token = jwt.encode({
                    'user': check_email["email"],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=int(req.form["duration"]))}
                    ,tokenSecret.value, algorithm="HS256")
            
                logging.info(tokenSecret.value)

                body= {
                    'user': json.dumps(check_email),
                    'userId': json.dumps(check_email["id"]),
                    'token': token
                }

                return func.HttpResponse(json.dumps(body), status_code=201)

            except ValueError:
                return func.HttpResponse("some information missing")