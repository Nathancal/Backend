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

    user_db = cosmosClient.get_database_client('users')
    user_container = user_db.get_container_client('user')

    email = str(req.form["email"])
    password = str(req.form["password"])

    hash = str(bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(rounds=10)))
    splitHash = hash.split("'", 3)


    query = "SELECT * FROM user WHERE user.email=@email"

    check_user = list(user_container.query_items(
        query=query,
        parameters=[{
            "name":"@email", "value": email
        }],
        enable_cross_partition_query=True
    ))

    logging.info(check_user)

    if check_user:

        return func.HttpResponse("A user with this email already exists", status_code=409)
        
    id = uuid.uuid4().hex

    createUser = {
        'id': id,
        'email': email,
        'password': str(splitHash[1]),
        'forename': req.form["forename"],
        'surname': req.form["surname"],
        'admin': False     
    }

    try:
        tokenSecret = config_client.get_configuration_setting(key='token-secret')
        returnUser = user_container.create_item(createUser)

        token = jwt.encode({
            'user': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=int(req.form["duration"]))}
            ,tokenSecret.value, algorithm="HS256")

    except ValueError:
        return func.HttpResponse( "some information is missing please try again")

    body = {
        'user': json.dumps(returnUser),
        'token': token
    }
    return func.HttpResponse(json.dumps(body), status_code=201)
   
