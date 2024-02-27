from unittest import TestCase
from data_models import BotInput, LanguageInput, LanguageIntent, MessageData, MessageType


class TestWA(TestCase):
    def test_data_model(self):
        data = {
            "source": "flow",
            "session_id": "f3126ced-637b-417e-9a48-92ca9c396144",
            "message_id": None,
            "turn_id": "1d1997f8-3598-46b5-93b3-46fa780eb727",
            "intent": "language_out",
            "data": {
                "message_type": "interactive",
                "message_data": {
                    "message_text": "Welcome to Nyaya Setu Chatbot, by the Department of Justice, Government of India. Here you can find answers to frequently asked legal queries. You can also use me to connect to an advocate to ask your legal queries. I can also generate some selected legal documents based on your requirements. Please choose an option below:",
                    "media_url": None,
                },
                "options_list": [
                    {"id": "1", "title": "Ask Legal Query"},
                    {"id": "2", "title": "Talk Advocate(Free)"},
                    {"id": "3", "title": "Legal Document"},
                ],
                "document": None,
                "wa_screen_id": None,
                "wa_flow_id": None,
                "header": "header",
                "footer": "footer",
                "menu_selector": None,
                "menu_title": None,
                "form_token": None,
            },
        }
        language_input = LanguageInput(**data)
        # print(language_input)
        print(language_input.data.options_list)

    def test_data_model_input(self):
        data = {
            "source": "flow",
            "session_id": "f3126ced-637b-417e-9a48-92ca9c396144",
            "message_id": None,
            "turn_id": "1d1997f8-3598-46b5-93b3-46fa780eb727",
            "intent": "language_in",
            "data": {
                "message_type": "interactive",
                "message_data": {
                    "message_text": "Welcome to Nyaya Setu Chatbot, by the Department of Justice, Government of India. Here you can find answers to frequently asked legal queries. You can also use me to connect to an advocate to ask your legal queries. I can also generate some selected legal documents based on your requirements. Please choose an option below:",
                    "media_url": None,
                }
            },
        }
        language_input = LanguageInput(**data)
        # print(language_input)
        print(language_input.data)

    def test_data_model_language_input(self):
        session_id = '123'
        msg_id = '123'
        turn_id = '123'
        message_type = MessageType.TEXT
        message_data = MessageData(
            message_text="Hi",
            media_url=None,
        )
        language_input = LanguageInput(
                    source="channel",
                    session_id=session_id,
                    message_id=msg_id,
                    turn_id=turn_id,
                    intent=LanguageIntent.LANGUAGE_IN.value,
                    data=BotInput(
                        message_type=message_type,
                        message_data=message_data,
                    ),
                )
        # print(language_input)
        print(language_input)

