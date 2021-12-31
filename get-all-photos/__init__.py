import logging
import json
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import ContainerClient
from azure.storage.blob._shared.base_client import _LOGGER


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')

def main(req: func.HttpRequest) -> func.HttpResponse:


    db = cosmosClient.get_database_client('photo')
    container = db.get_container_client('images')

    query = "SELECT * FROM images"

    image_list = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    logging.info(image_list)
        
    return func.HttpResponse(json.dumps(image_list), mimetype="application/json", status_code=200)
