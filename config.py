#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json
""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """
    def __init__(self, configFile:str) -> None:
        try:
            with open(configFile, 'r') as config:
                jsonConfigData = json.load(config)

            self.PORT = jsonConfigData["port"]
            self.APP_ID = jsonConfigData["MicrosoftAppId"]
            self.APP_PASSWORD = jsonConfigData["MicrosoftAppPassword"]

            # Azure QnA Maker related config details
            self.QNA_KNOWLEDGEBASE_ID = jsonConfigData["QnAKnowledgebaseId"]
            self.QNA_ENDPOINT_KEY = jsonConfigData["QnAEndpointKey"]
            self.QNA_ENDPOINT_HOST = jsonConfigData["QnAEndpointHostName"]
            
            # Azure LUIS related config details
            self.LUIS_APP_ID = jsonConfigData["LuisAppId"]
            self.LUIS_API_KEY = jsonConfigData["LuisAPIKey"]
            # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
            self.LUIS_API_HOST_NAME = jsonConfigData["LuisAPIHostName"]

            # Azure Cosmos DB related config details
            self.COSMOS_DB_ENDPOINT = jsonConfigData["cosmoDbEndpoint"]
            self.COSMOS_DB_AUTHKEY = jsonConfigData["cosmoDbAuthKey"]
            self.COSMOS_DB_DATABASE = jsonConfigData["cosmoDbDatabase"]
            self.COSMOS_DB_SAVINGS_CONTAINER = jsonConfigData["cosmoDbSavingsContainer"]
            self.COSMOS_DB_CURRENTS_CONTAINER = jsonConfigData["cosmoDbCurrentsContainer"]
            self.COSMOS_DB_SAVINGS_PARTITIONKEY = jsonConfigData["cosmoDbSavingsPartitionKey"]
            self.COSMOS_DB_CURRENTS_PARTITIONKEY = jsonConfigData["cosmoDbCurrentsPartitionKey"]
            
            # Azure translator related config details
            self.TRANSLATOR_SUBSCRIPTIONKEY = jsonConfigData["translatorSubscriptionKey"]
            self.TRANSLATOR_ENDPOINT = jsonConfigData["translatorEndpoint"]
            self.TRANSLATOR_LOCATION = jsonConfigData["translatorLocation"]
        except Exception as e:
            print(e)
            raise Exception("Error in DefaultConfig Class")

 