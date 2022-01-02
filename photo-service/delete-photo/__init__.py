import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import ContainerClient


endpoint = "https://cosmosdbcom682.documents.azure.com:443/"
key = 'UZ2HCpT6Y0BSqgBXuMJrKpXWFnuu3LhT8swGigQhMdaVPkUwY74GW5KXacrvWQve4L2BXrCjh5mVqPNAkAl9rA=='
cosmosClient = CosmosClient(endpoint, key)
partition_key = PartitionKey(path='/id')


def main(req: func.HttpRequest) -> func.HttpResponse:

    try:
        image_container = ContainerClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=ulsterphotostore;AccountKey=VhW+zCGui/nt0AJv3XEzYJUMjEhlVIEO7w0uFctJeP4G3l/zeAsiWg3HJEYxviDXlJJpG8CgGkAMYioyP/iRPQ==;EndpointSuffix=core.windows.net", container_name="imagestorecontainer")

        Id = req.form["Id"]

        image_container.delete_blob(blob=Id)  
        db = cosmosClient.get_database_client('photo')
        container = db.get_container_client('images')
        container.delete_item("dbs/photo/colls/images/docs/"+ Id)

        return func.HttpResponse("item successfully deleted", status_code=204)

    except KeyError:
        return func.HttpResponse("item not found")


