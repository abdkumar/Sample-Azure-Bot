
import requests
import uuid
import json
from config import DefaultConfig


class AzureTranslator:
    '''
    Using Azure translator service
    '''
    def __init__(self, config: DefaultConfig) -> None:
        # Add your subscription key and endpoint
        self.subscription_key = config.TRANSLATOR_SUBSCRIPTIONKEY
        self.endpoint = config.TRANSLATOR_ENDPOINT

        # Add your location, also known as region. The default is global.
        # This is required if using a Cognitive Services resource.
        self.location = config.TRANSLATOR_LOCATION

        path = '/detect'
        self.detect_url = self.endpoint + path

        self.params = {
            'api-version': '3.0'
        }

        path = '/translate'
        self.translate_url = self.endpoint + path
        # https://api.cognitive.microsofttranslator.com/translate?api-version=3.0
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Ocp-Apim-Subscription-Region': self.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

    def translate(self, text: str, fromLang: str, toLang: list):
        result = dict()
        # You can pass more than one object in body.
        body = [{
            'text': text
        }]
        params = self.params.copy()
        params.update({
            'from': fromLang,
            'to': toLang
        })

        request = requests.post(
            self.translate_url, params=params, headers=self.headers, json=body)
        if request.status_code == 200:
            response = request.json()
            # print(json.dumps(response, sort_keys=True,
            #                  ensure_ascii=False, indent=4, separators=(',', ': ')))
            for each_lang in response[0]['translations']:
                result[each_lang["to"]] = each_lang["text"]
            return result
        else:
            raise Exception(request.status_code)

    def detect_language(self, text: str) -> str:
        # You can pass more than one object in body.
        body = [
            {'text': text
             }]

        request = requests.post(
            self.detect_url, params=self.params, headers=self.headers, json=body)
        if request.status_code == 200:
            response = request.json()
            return response[0]['language']
            # print(json.dumps(response, sort_keys=True,
            #       ensure_ascii=False, indent=4, separators=(',', ': ')))
        else:
            raise Exception(request.status_code)


# obj1 = AzureTranslator()
# # obj1.translate(
# #     "ನಿಮ್ಮ ಕಾರನ್ನು ಬ್ಲಾಕ್ ನ ಸುತ್ತಲೂ ಕೆಲವು ಬಾರಿ ಓಡಿಸಲು ನಾನು ನಿಜವಾಗಿಯೂ ಬಯಸುತ್ತೇನೆ.", 'kn', ['en'])
# print(obj1.detect_language("ನಿಮ್ಮ ಕಾರನ್ನು ಬ್ಲಾಕ್ ನ ಸುತ್ತಲೂ ಕೆಲವು ಬಾರಿ"))
