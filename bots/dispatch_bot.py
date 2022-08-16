# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from botbuilder.ai.luis import LuisApplication, LuisRecognizer, LuisPredictionOptions
from botbuilder.core import ActivityHandler, TurnContext, ConversationState
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from botbuilder.azure import CosmosDbStorage

from config import DefaultConfig
from bots.utils import Utils
from bots.azure_translator import AzureTranslator

from typing import List
import uuid


class DispatchBot(ActivityHandler):
    SAVINGS_ADAPTIVE_CARD_PATH = "Cards/savings_adaptive_card.json"
    CURRENT_ADAPTIVE_CARD_PATH = "Cards/current_adaptive_card.json"

    def __init__(self, constate: ConversationState,
                 cosDb: CosmosDbStorage,
                 config: DefaultConfig
                 ):
        self.constate = constate
        self.cosmodb = cosDb
        self.config = config
        self.cosmodb.__container_link1 = "dbs/" + self.cosmodb.config.database + \
            "/colls/" + self.config.COSMOS_DB_SAVINGS_CONTAINER
        self.cosmodb.__container_link2 = "dbs/" + self.cosmodb.config.database + \
            "/colls/" + self.config.COSMOS_DB_CURRENTS_CONTAINER

        self.conprop = self.constate.create_property("constate")
        # If the includeApiResults parameter is set to true, as shown below, the full response
        # from the LUIS api will be made available in the properties  of the RecognizerResult
        luis_application = LuisApplication(
            config.LUIS_APP_ID,
            config.LUIS_API_KEY,
            "https://" + config.LUIS_API_HOST_NAME,
        )

        luis_options = LuisPredictionOptions(
            include_all_intents=True, include_instance_data=True
        )
        self.recognizer = LuisRecognizer(luis_application, luis_options, True)

        # configure translation service
        self.azure_translator = AzureTranslator(self.config)

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self.constate.save_changes(turn_context)

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Welcome to ABC Bank\n.How can I help you?".format())

    async def on_message_activity(self, turn_context: TurnContext):
        if turn_context.activity.text != None:
            # detect the language and translate if it is non-english
            detect_language = self.azure_translator.detect_language(
                turn_context.activity.text)
            if detect_language != 'en':
                tralnsation_result = self.azure_translator.translate(
                    turn_context.activity.text, detect_language, ['en'])
                turn_context.activity.text = tralnsation_result['en']
                print(turn_context.activity.text)
            # First, we use the dispatch model to determine which cognitive service (LUIS or QnA) to use.
            recognizer_result = await self.recognizer.recognize(turn_context)

            # Top intent tell us which cognitive service to use.
            intent = LuisRecognizer.top_intent(
                recognizer_result, min_score=0.5)

            # Next, we call the dispatcher with the top intent.
            await self._dispatch_to_top_intent(turn_context, intent)
        # if value is not None and PAN key pressent in the values -> SavingsAccount
        if (turn_context.activity.value != None) and ("PAN" in turn_context.activity.value):
            result = turn_context.activity.value
            end_message = self.savingsAccountToCosmosDB(result)
            await turn_context.send_activity(end_message)

        # if value is not None and GST key pressent in the values -> CurrentAccount
        if (turn_context.activity.value != None) and ("GST" in turn_context.activity.value):
            result = turn_context.activity.value
            end_message = self.currentAccountToCosmosDB(result)
            await turn_context.send_activity(end_message)

    def savingsAccountToCosmosDB(self, turn_context_values):
        cosmosItem = dict()
        cosmosItem["id"] = str(uuid.uuid4())
        cosmosItem["Name"] = turn_context_values["Name"]
        cosmosItem["DOB"] = turn_context_values["DOB"]
        cosmosItem["Mobile"] = turn_context_values["Mobile"]
        cosmosItem["Email"] = turn_context_values["Email"]
        cosmosItem["PAN"] = turn_context_values["PAN"]
        address = turn_context_values.get("Street", "") + "," + turn_context_values.get("City", "") + "," +\
            turn_context_values.get("State", "")
        cosmosItem["Address"] = address
        cosmosItem["Pincode"] = turn_context_values["Pincode"]

        # check if pan is already registered
        pan = cosmosItem["PAN"]
        query = f'SELECT * FROM c WHERE c.PAN = "{pan}"'
        results = self.cosmodb.client.QueryItems(
            database_or_Container_link=self.cosmodb.__container_link1,
            query=query,
            options={"enableCrossPartitionQuery": True},
            partition_key=self.config.COSMOS_DB_SAVINGS_PARTITIONKEY)

        # if query items length is 0 -> PAN is not present
        # then insert the item to container
        if len(list(results)) == 0:
            self.cosmodb.client.UpsertItem(
                self.cosmodb.__container_link1, cosmosItem)
            return f"{cosmosItem['Name']} - Thanks for opening Savings account with us"
        else:
            return f"PAN - {pan} is already registered"

    def currentAccountToCosmosDB(self, turn_context_values):
        cosmosItem = dict()
        cosmosItem["id"] = str(uuid.uuid4())
        cosmosItem["CompanyName"] = turn_context_values["FirmName"]
        cosmosItem["CompanyType"] = turn_context_values["FirmType"]
        cosmosItem["DOF"] = turn_context_values["DOF"]
        cosmosItem["Mobile"] = turn_context_values["Mobile"]
        cosmosItem["Email"] = turn_context_values["Email"]
        cosmosItem["GSTIN"] = turn_context_values["GST"]
        cosmosItem["City"] = turn_context_values.get("City", "")
        cosmosItem["State"] = turn_context_values.get("State", "")
        cosmosItem["Pincode"] = turn_context_values["Pincode"]

        # check if pan is already registered
        gst = cosmosItem["GSTIN"]
        query = f'SELECT * FROM c WHERE c.GSTIN= "{gst}"'
        results = self.cosmodb.client.QueryItems(
            database_or_Container_link=self.cosmodb.__container_link2,
            query=query,
            options={"enableCrossPartitionQuery": True},
            partition_key=self.config.COSMOS_DB_CURRENTS_PARTITIONKEY)

        # if query items length is 0 -> GST is not present
        # then insert the item to container
        if len(list(results)) == 0:
            self.cosmodb.client.UpsertItem(
                self.cosmodb.__container_link2, cosmosItem)
            return f"{cosmosItem['CompanyName']} - Thanks for opening Current Account with us"
        else:
            return f"GSTIN - {gst} is already registered"

    async def _dispatch_to_top_intent(
            self, turn_context: TurnContext, intent):
        # process flow based on intent type
        if intent == "SavingsAccount":
            await self._process_savings_account(turn_context)
        elif intent == "CurrentAccount":
            await self._process_current_account(turn_context)
        else:
            await turn_context.send_activity("Sorry, I didn't get that. Please be more specific")

    async def _process_savings_account(self, turn_context: TurnContext):
        # generate adaptive card for Savings Account form
        message = Activity(
            text="Showing Savings Account form",
            type=ActivityTypes.message,
            attachments=[Utils.create_adaptive_card_attachment(DispatchBot.SAVINGS_ADAPTIVE_CARD_PATH)])

        await turn_context.send_activity(message)

    async def _process_current_account(self, turn_context: TurnContext):
        # generate adaptive card for Current  Account form
        message = Activity(
            text="Showing Current Account form",
            type=ActivityTypes.message,
            attachments=[Utils.create_adaptive_card_attachment(DispatchBot.CURRENT_ADAPTIVE_CARD_PATH)])

        await turn_context.send_activity(message)
