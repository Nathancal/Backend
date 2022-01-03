import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
import uuid
import json
import datetime
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
    try:


        post_title = req.form["postTitle"]
        post_body = req.form["postBody"]
        user_id = req.form["userId"]

        if req.form["mediaUrl"]:
            media_url = req.form["mediaUrl"]
            media_title = req.form["mediaTitle"]

            post = {
                'id': uuid.uuid4().hex,
                'userId': user_id,
                'title': post_title,
                'body': post_body,
                'date': datetime.datetime.utcnow().isoformat(),
                'mediaUrl': media_url,
                'mediaTitle': media_title
            }
        else:
            post = {
                'id': uuid.uuid4().hex,
                'userId': user_id,
                'title': post_title,
                'body': post_body,
                'date': datetime.datetime.utcnow().isoformat()
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


      