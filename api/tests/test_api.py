import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from app.main import app, produce_message, encrypt_text, encrypt_dict
from cryptography.fernet import Fernet
from app.jb_schema import JBBotUpdate, JBBotConfig, JBBotActivate, JBBotCode


# Mock environment variables
os.environ["KAFKA_CHANNEL_TOPIC"] = "test_channel_topic"
os.environ["KAFKA_FLOW_TOPIC"] = "test_flow_topic"
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()
producer = "jb"

def client():
    return AsyncClient(app=app, base_url="http://test")

@pytest.mark.asyncio
async def test_read_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.asyncio
async def test_get_bots(client):
    # TODO: Confirm the JBBot object structure
    bot_list = [
        {
            "id": "bot1",
            "name": "Test Bot 1",
            "phone_number": "1234567890",
            "status": "active",
            "config_env": {"existing_key": "existing_value"},
            "version": "1.0.0",
            "channels": ["whatsapp"]
        },
        {
            "id": "bot2",
            "name": "Test Bot 2",
            "phone_number": "0987654321",
            "status": "inactive",
            "config_env": {"another_key": "another_value"},
            "version": "1.1.0",
            "channels": ["telegram"]
        }
    ]
    
    # Mock the get_bot_list function
    mock_get_bot_list = AsyncMock(return_value=bot_list)
    with patch("app.main.get_bot_list", mock_get_bot_list):
        # Send a GET request to the /bots endpoint
        response = await client.get("/bots")
        
        # Verify the response status code and data
        assert response.status_code == 200
        assert response.json() == bot_list

@pytest.mark.asyncio
async def test_update_bot_data(client):
# understand how the bot data is stored in db
    bot_id = "bot1"
    update_fields = JBBotUpdate(config_env={"key": "value"})

    # mock data
    mock_bot = {
        "id": bot_id,
        "name": "Test Bot",
        "phone_number": "1234567890",
        "status": "inactive",
        "config_env": {"existing_key": "existing_value"},
        "version": "1.0.0",
        "channels": ["whatsapp"]
    }
    
    mock_get_bot_by_id = AsyncMock(return_value=mock_bot)
    mock_update_bot = AsyncMock()

    with patch("app.main.get_bot_by_id", mock_get_bot_by_id):
        with patch("app.main.update_bot", mock_update_bot):
            response = await client.patch(f"/bot/{bot_id}", json=update_fields.dict(exclude_unset=True))
            assert response.status_code == 200
            mock_update_bot.assert_called_once_with(bot_id, {
                "config_env": {
                    "key": encrypt_text("value")
                }
            })
            returned_bot = response.json()
            assert returned_bot["id"] == bot_id
            assert "config_env" in returned_bot

