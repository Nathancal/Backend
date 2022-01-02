import logging
import uuid
import jwt
import json
import bcrypt
import datetime
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting

endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
appConfigConnString = 'Endpoint=https://cloudappconfig.azconfig.io;Id=hMS5-l0-s0:b0XuE4FK+lXhmMzk4Lf7;Secret=r3vuyYTIvaT6rHScd3M0qpV00YtDXrBtGjqqgpwhFpA='
config_client = AzureAppConfigurationClient.from_connection_string(appConfigConnString)
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
                tokenSecret = config_client.get_configuration_setting(key='token-secret')

                token = jwt.encode({
                    'user': check_email["email"],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=int(req.form["duration"]))}
                    ,tokenSecret.value, algorithm="HS256")
            
                body= {
                    'user': json.dumps(check_email),
                    'userId': json.dumps(check_email["id"]),
                    'token': token
                }

                return func.HttpResponse(json.dumps(body), status_code=201)

            except ValueError:
                return func.HttpResponse("some information missing")