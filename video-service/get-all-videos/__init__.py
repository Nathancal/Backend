import logging
import json
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')

def main(req: func.HttpRequest) -> func.HttpResponse:


    db = cosmosClient.get_database_client('videos')
    container = db.get_container_client('video')

    query = "SELECT * FROM video"

    video_list = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    logging.info(video_list)

    header = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET,POST'
    }
        
    return func.HttpResponse(json.dumps(video_list), headers=header, mimetype="application/json", status_code=200)
