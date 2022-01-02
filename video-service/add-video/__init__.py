import logging
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

