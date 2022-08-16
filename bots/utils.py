
import json
from botbuilder.core import CardFactory
from botbuilder.schema import Attachment


class Utils:

    @staticmethod
    def create_adaptive_card_attachment(card_path: str) -> Attachment:
        """
        Load a random adaptive card attachment from file.
        :return:
        """
        with open(card_path, "rb") as in_file:
            card_data = json.load(in_file)

        return CardFactory.adaptive_card(card_data)
