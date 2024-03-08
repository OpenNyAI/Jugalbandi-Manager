import unittest
from unittest.mock import patch, AsyncMock, MagicMock, Mock  # Import AsyncMock for async methods
from fastapi.testclient import TestClient
from main import app
import asyncio
import unittest

class TestMain(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app, base_url="http://test")
        self.mock_send_message = patch('main.producer.send_message').start()
        self.mock_logger = patch('main.logger').start() 

    @patch('main.get_bot_list')  # Patch where get_bot_list is actually called
    async def test_get_bots(self, mock_get_bot_list):
        #empty bot list
        mock_get_bot_list.return_value = []
        response = self.client.get('/bots')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        #non-empty bot list
        mock_get_bot_list.return_value = [{'id': '123', 'name': 'test'}]
        response = self.client.get('/bots')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{'id': '123', 'name': 'test'}])

    @patch('main.get_plugin_reference')
    @patch('main.produce_message')
    async def test_webhook(self, mock_produce_message, mock_get_plugin_reference):
        plugin_reference_mock = AsyncMock()
        plugin_reference_mock.id = "test_uuid"
        plugin_reference_mock.session_id = "test-session-id"
        plugin_reference_mock.turn_id = "test-turn-id"
        mock_get_plugin_reference.return_value = plugin_reference_mock
        response = self.client.post('/webhook', json={'uuid': 'jbkeytest_uuidjbkey'})
        
        self.assertEqual(response.status_code, 200)
        mock_get_plugin_reference.assert_called_once()
        mock_produce_message.assert_called_once()



    
    def tearDown(self):
        super().tearDown()
        patch.stopall()


   

if __name__ == '__main__':
    unittest.main()
