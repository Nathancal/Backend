import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
import json
from token_required import jwt_required

logging.Logger.root.level = 10


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')

db_name = 'posts'
db = cosmosClient.create_database_if_not_exists(id=db_name)

cont_name = 'post'
cosmosContainer = db.create_container_if_not_exists(
    id=cont_name,
    partition_key=partition_key,
    offer_throughput=400
)

@jwt_required
def main(req: func.HttpRequest) -> func.HttpResponse:

    db = cosmosClient.get_database_client('posts')
    container = db.get_container_client('post')
 
    userId = req.form["userId"]

    query = "SELECT * FROM post WHERE post.userId=@userId ORDER BY post.date DESC"

    user_post_list = list(container.query_items(
        query=query,
        parameters=[{
            "name":"@userId", "value": userId
        }],
        enable_cross_partition_query=True
    ))

    logging.info(user_post_list)

    header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET,POST'
    }
        
    return func.HttpResponse(json.dumps(user_post_list), headers=header, mimetype="application/json", status_code=200)