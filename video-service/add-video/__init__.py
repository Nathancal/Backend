import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey, partition_key
from azure.storage.blob import BlobServiceClient, BlobClient
import uuid
import json

logging.Logger.root.level = 10


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)

blobService = BlobServiceClient(account_url="https://ulstervideostore.blob.core.windows.net/videos?sp=rad&st=2022-01-02T16:46:19Z&se=2025-01-03T00:46:19Z&spr=https&sv=2020-08-04&sr=c&sig=grBTSBqt2CtL2%2BXb8AgYnBXx88XbvQ%2FG6EYobx33yRA%3D")
partition_key = PartitionKey(path='/id')

db_name = 'videos'
db = cosmosClient.create_database_if_not_exists(id=db_name)

cont_name = 'video'
cosmosContainer = db.create_container_if_not_exists(
    id=cont_name,
    partition_key=partition_key,
    offer_throughput=400
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

        videoId = uuid.uuid4().hex

        blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=ulstervideostore;AccountKey=5MZNKoHbZLVcRvH4RdlnUitC7GW58wL8tYXGql/EW30WcSdBchbx6BsFbDcqgorY3H1rA3r3KFf2BILWkZlEmA==;EndpointSuffix=core.windows.net", container_name="videos", blob_name=blobId)

        videoUpload = req.files["File"]
        filestream = videoUpload.stream
        filestream.seek(0)

        blob.upload_blob(filestream.read(), blob_type="BlockBlob")
        urlForCosmos = blob.url

        if blob.url is None:
            return  func.HttpResponse("unable to create blob try again", status_code=409)

        videoData = {
            'fileLocator':videoId,
            'filePath': urlForCosmos,
            'id': videoId,
            'fileName': req.form["FileName"],
            'fileType': req.form["FileType"],
            'userId': req.form['userId']
        }

        cosmosContainer.create_item(videoData)

        resObj = {
        "message": "image successfully posted"
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


      