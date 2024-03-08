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
        sample_bot_list = [
            {
                "id": "1234",
                "name": "My Bot",
                "phone_number": "9952741113",
                "status": "active",
                "dsl": "Some DSL",
                "code": "Some Code",
                "requirements": "requirements.txt content",
                "index_urls": ["http://example.com"],
                "config_env": {"API_URL": "http://api.example.com"},
                "required_credentials": ["API_KEY", "API_SECRET"],
                "credentials": {"API_KEY": "key123", "API_SECRET": "secret123"},
                "version": "0.0.1",
                "channels": ["whatsapp", "telegram"],
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-02T00:00:00.000Z"
            }
        ]
        mock_get_bot_list.return_value = sample_bot_list
        response = self.client.get('/bots')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),sample_bot_list)
    
    @patch('main.get_bot_by_id')
    @patch('main.update_bot')
    @patch('main.encrypt_text')
    async def test_update_bot_data(self,mock_encrypt_text, mock_update_bot, mock_get_bot_by_id):
        bot_id = "1234"
        update_data = {
            "name": "Updated Bot",
            "config_env": {"API_URL": "http://api.example.com"}
        }
        mock_bot = {
            "name": "My Bot",
            "phone_number": "91987654321",
            "status": "active",
            "dsl": "Some DSL",
            "code": "Some Code"
        }
        mock_encrypt_text.return_value = "encrypted_text"
        mock_get_bot_by_id.return_value = mock_bot
        mock_update_bot.return_value = mock_bot.update(update_data)
        response = self.client.patch(f'/bot/{bot_id}', json=update_data)
        print(response)
        self.assertEqual(response.status_code, 200)
        mock_get_bot_by_id.assert_called_once_with(bot_id)
        expected_update_data = update_data.copy()
        expected_update_data['config_env'] = {"API_URL": "encrypted_text"}
        mock_update_bot.assert_awaited_with(bot_id, expected_update_data)
        self.assertEqual(response.json()['name'], update_data['name'])
    
    @patch('main.get_bot_by_id')
    async def test_update_bot_data_not_found(self, mock_get_bot_by_id):
        bot_id = "nonexistent"
        update_data = {
            "name": "Updated Bot"
        }
        # Mocking the get_bot_by_id to return None for a nonexistent bot
        mock_get_bot_by_id.return_value = None

        # Make a patch request to the /bot/{bot_id} endpoint with a nonexistent bot_id
        response = self.client.patch(f"/bot/{bot_id}", json=update_data)

        # Assert the response status code is 404 (Not Found)
        assert response.status_code == 404

        # Assert the correct error message is returned
        assert response.json()["detail"] == "Bot not found"

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
