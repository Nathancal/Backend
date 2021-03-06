import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
import json
from token_required import jwt_required

logging.Logger.root.level = 10


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')

@jwt_required
def main(req: func.HttpRequest) -> func.HttpResponse:

    db = cosmosClient.get_database_client('following')
    container = db.get_container_client('following')

    userId = req.form["userId"]

    query = "SELECT follows FROM following WHERE following.userId=@userId"

    get_follows_list = list(container.query_items(
        query=query,
        parameters=[{
            "name":"@userId", "value": userId
        }],
        enable_cross_partition_query=True
    ))

    logging.info(get_follows_list)
        

    header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET,POST'
    }
        
    return func.HttpResponse(json.dumps(get_follows_list), headers=header, mimetype="application/json", status_code=200)