from functools import wraps
import logging
import re
import azure.functions as httpReqFunc
import jwt
import json
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting

keyvaultURI = 'Endpoint=https://cloudappconfig.azconfig.io;Id=C+TH-l0-s0:8eSYgWDN0V7IVttSB7Mf;Secret=QF7Lpj630DCyIn5gXyLCd6djdf1GGjWBQwHbkwQD/0g='
app_config_client = AzureAppConfigurationClient.from_connection_string(keyvaultURI)

def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(req: httpReqFunc.HttpRequest, *args, **kwargs):
       
        logging.info(req.headers.get("x-access-token"))

        token = None

        if 'x-access-token' in req.headers:
            token = req.headers['x-access-token']

        if not token:

            resObj = {"message": "Token is missing"}

            return httpReqFunc.HttpResponse(json.dumps(resObj),status_code=401)

        try:

            token_secret = app_config_client.get_configuration_setting(key='token-secret')


            data = jwt.decode(str(token), token_secret.value, algorithms="HS256")

        except:
            
            resObj = {"message": "Token is invalid"}

            return httpReqFunc.HttpResponse(json.dumps(resObj), status_code=401)


        return func(req, *args, **kwargs)

    return jwt_required_wrapper
