import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
import json

logging.Logger.root.level = 10


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')


def main(req: func.HttpRequest) -> func.HttpResponse:

    db = cosmosClient.get_database_client('users')
    container = db.get_container_client('user')

    userId = req.form["userId"]

    query = "SELECT * FROM user WHERE user.userId=@userId"

    get_user_by_id = list(container.query_items(
        query=query,
        parameters=[{
            "name":"@userId", "value": userId
        }],
        enable_cross_partition_query=True
    ))

    logging.info(get_user_by_id)

    header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET,POST'
    }
        
    return func.HttpResponse(json.dumps(get_user_by_id), headers=header, mimetype="application/json", status_code=200)