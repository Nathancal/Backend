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

blobService = BlobServiceClient(account_url="https://ulsterphotostore.blob.core.windows.net/imagestorecontainer?sp=r&st=2021-12-30T22:16:39Z&se=2022-01-14T06:16:39Z&spr=https&sv=2020-08-04&sr=c&sig=OvBFgaavvBJsqi7%2BNoAdUEpA6rsE77t78t9npiG2elg%3D")
partition_key = PartitionKey(path='/id')

db_name = 'photo'
db = cosmosClient.create_database_if_not_exists(id=db_name)

cont_name = 'images'
cosmosContainer = db.create_container_if_not_exists(
    id=cont_name,
    partition_key=partition_key,
    offer_throughput=400
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:

        blobId = uuid.uuid4().hex

        blob = BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=ulsterphotostore;AccountKey=VhW+zCGui/nt0AJv3XEzYJUMjEhlVIEO7w0uFctJeP4G3l/zeAsiWg3HJEYxviDXlJJpG8CgGkAMYioyP/iRPQ==;EndpointSuffix=core.windows.net", container_name="imagestorecontainer", blob_name=blobId)

        imageUpload = req.files["File"]
        filestream = imageUpload.stream
        filestream.seek(0)

        blob.upload_blob(filestream.read(), blob_type="BlockBlob")
        urlForCosmos = blob.url

        if blob.url is None:
            return  func.HttpResponse("unable to create blob try again", status_code=409)

        imageData = {
            'fileLocator':blobId,
            'filePath': urlForCosmos,
            'id': blobId,
            'fileName': req.form["FileName"],
            'userId': req.form['userID']
        }

        cosmosContainer.create_item(imageData)

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


      
