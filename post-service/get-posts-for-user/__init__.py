import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
from azure.storage.blob import BlobServiceClient, BlobClient
import uuid
import json
import datetime

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


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:


        post_title = req.form["postTitle"]
        post_body = req.form["postBody"]
        post_date = datetime.datetime.utcnow()
        media_url = req.form["mediaUrl"]
        media_title = req.form["mediaTitle"]
        user_id = req.form["userId"]

        post = {
            'id': uuid.uuid4().hex,
            'userId': user_id,
            'title': post_title,
            'body': post_body,
            'date': post_date,
            'mediaUrl': media_url,
            'mediaTitle': media_title
        }
        cosmosContainer.create_item(post)

        resObj = {
        "message": "post successfully created.",
        "data": json.dumps(post)
        }

        return func.HttpResponse(json.dumps(resObj), status_code=201)
    except ValueError:
        
        resObj = {
        "message": "Value Error"
        }
        return func.HttpResponse(json.dumps(resObj), status_code=500)
    except RuntimeError:
        resObj = {
        "message": "Runtime error"
        }
        return func.HttpResponse(json.dumps(resObj), status_code=500)


      