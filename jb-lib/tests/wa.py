from unittest import TestCase

from whatsapp import WhatsappHelper


class TestWA(TestCase):

    def test_parse_text(self):
        message = {"object": "whatsapp_business_account", "entry": [{"id": "112776635030672", "changes": [{"value": {"messaging_product": "whatsapp", "metadata": {"display_phone_number": "919711028566", "phone_number_id": "116346771524855"}, "contacts": [{"profile": {
            "name": "Sameer Segal"}, "wa_id": "919886689754"}], "messages": [{"from": "919886689754", "id": "wamid.HBgMOTE5ODg2Njg5NzU0FQIAEhgUM0E0RjQ2QzQyMUUxREYyODcxNjQA", "timestamp": "1705550692", "text": {"body": "Hey"}, "type": "text"}]}, "field": "messages"}]}]}
        for data in WhatsappHelper.process_messsage(message):
            print(data)
            # print()
            # print(number)
            # for obj in data.get_msg_list():
            #     print(obj.time)
            #     print(obj.msgtype)
            #     print(obj.content)

            # {'from': '919886689754', 'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAEhgUM0E5Q0UzOTNGQzJFRTNCNjhDRDMA', 'timestamp': '1705638208', 'type': 'audio', 'audio': {'mime_type': 'audio/ogg; codecs=opus', 'sha256': 'YjZyxaG+/GBvAkBe1np5JD46YexkBtNFZmZRNcFkPtw=', 'id': '683752867293692', 'voice': True}}
    
    def test_parse_audio(self):
        message = {'object': 'whatsapp_business_account', 'entry': [{'id': '112776635030672', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '919711028566', 'phone_number_id': '116346771524855'}, 'contacts': [{'profile': {'name': 'Sameer Segal'}, 'wa_id': '919886689754'}], 'messages': [{'from': '919886689754', 'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAEhgUM0E5Q0UzOTNGQzJFRTNCNjhDRDMA', 'timestamp': '1705638208', 'type': 'audio', 'audio': {'mime_type': 'audio/ogg; codecs=opus', 'sha256': 'YjZyxaG+/GBvAkBe1np5JD46YexkBtNFZmZRNcFkPtw=', 'id': '683752867293692', 'voice': True}}]}, 'field': 'messages'}]}]}
        for data in WhatsappHelper.process_messsage(message):
            print(data)
        # {'from': '919886689754', 'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAEhgUM0FGMzlCRjMwODNDMzlEMjZEMkIA', 'timestamp': '1706020352', 'type': 'interactive', 'interactive': {'type': 'list_reply', 'list_reply': {'id': 'lang_hindi', 'title': 'हिन्दी'}}}

    def test_parse_list_reply(self):
        message = {'object': 'whatsapp_business_account', 'entry': [{'id': '112776635030672', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '919711028566', 'phone_number_id': '116346771524855'}, 'contacts': [{'profile': {'name': 'Sameer Segal'}, 'wa_id': '919886689754'}], 'messages': [{'context': {'from': '919711028566', 'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAERgSNzdERjJCQTdFOTM1Q0MxMkQ3AA=='}, 'from': '919886689754', 'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAEhgUM0FGMzlCRjMwODNDMzlEMjZEMkIA', 'timestamp': '1706020352', 'type': 'interactive', 'interactive': {'type': 'list_reply', 'list_reply': {'id': 'lang_hindi', 'title': 'हिन्दी'}}}]}, 'field': 'messages'}]}]}
        for data in WhatsappHelper.process_messsage(message):
            print(data)
        # {'from': '919886689754', 'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAEhgUM0E0RjQ2QzQyMUUxREYyODcxNjQA', 'timestamp': '1705550692', 'type': 'text', 'text': {'body': 'Hey'}}
            
    def test_parse_status_messages(self):
        message = {'object': 'whatsapp_business_account', 'entry': [{'id': '112776635030672', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '919711028566', 'phone_number_id': '116346771524855'}, 'statuses': [{'id': 'wamid.HBgMOTE5ODg2Njg5NzU0FQIAERgSMTExQzhFQzMwRkUzREMxM0I3AA==', 'status': 'sent', 'timestamp': '1706027706', 'recipient_id': '919886689754', 'conversation': {'id': 'ede7a29f2f9cc1263caae929e036ed49', 'expiration_timestamp': '1706105820', 'origin': {'type': 'service'}}, 'pricing': {'billable': True, 'pricing_model': 'CBP', 'category': 'service'}}]}, 'field': 'messages'}]}]}
        for data in WhatsappHelper.process_messsage(message):
            print(data)
    
    def test_send_audio(self):
        mobile = '917408921252'
        audio_url = 'https://jbstudiotest.blob.core.windows.net/jbfiles/output_files/aeb28293-78d1-4ab6-ab3d-1983e8f45c6d.mp3?st=2024-01-25T11%3A02%3A27Z&se=2024-02-24T11%3A03%3A27Z&sp=r&sv=2023-11-03&sr=b&sig=XSKToQ//bNGN5VYyKW5nUjdiNlyzh60ERziTj7YHmtk%3D'
        status = WhatsappHelper.wa_send_audio_message(mobile, audio_url)
        print(status)