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
partition_key = PartitionKey(path='/userId')

db_name = 'comments'
db = cosmosClient.create_database_if_not_exists(id=db_name)

cont_name = 'comment'
cosmosContainer = db.create_container_if_not_exists(
    id=cont_name,
    partition_key=partition_key,
    offer_throughput=400
)

@jwt_required
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        userId = req.form["userId"]
  
        add_comment = {
            'id': uuid.uuid4().hex,
            'userId': userId,
            'postId': req.form["postId"],
            'comment': req.form["comment"],
            'date': datetime.datetime.utcnow().isoformat()
            
        }
        cosmosContainer.create_item(add_comment)

        resObj = {
        "message": "comment has been posted",
        "data": json.dumps(add_comment)
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