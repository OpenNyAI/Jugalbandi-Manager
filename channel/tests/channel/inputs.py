from unittest import TestCase
from channel.main import 

class TestChannelInputs(TestCase):

    def test_channel_inputs(self):
        self.assertTrue(True)


# Input Message
    # - channel, blob etc
    # bot_input - channel 
        # -- a) update_message() -- writes value to the DB
        # -- fetches credentials to fetch media file
        # -- writes to storage account
        # -- updates the url in the received_message
        # 
        # -- b) received_message


    # given a message write to language or flow
        # channel specific stuff -- out of scope
        # DB specific stuff -- out of scope
        # given a packate we correctly write to Language or Flow

        # tightly coupled with Channel & DB
            # you have to mock them

        def channel_processor(**args):
            return {
                'channel': 'slack',
                'message': 'Hello World'
            }
        
        def db_connection():
            return {
                'db': 'connection'
            }
        
        def send_message(**args):
            self.assertTrue('message' in args) 

        message = {
            ...
        }           

        process_incoming_message(msg, channel_processor, db_connection, send_message)

        def send_message(**args):
            self.assertTrue('message2' in args) 

        message2 = {
            ...
        }           

        process_incoming_message(msg2, channel_processor, db_connection, send_message)

    
    # - crud
# Output Message
# Crud - depends on the DB