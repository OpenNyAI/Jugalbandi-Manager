import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from app.main import app, produce_message, encrypt_text, encrypt_dict
from cryptography.fernet import Fernet
from app.jb_schema import JBBotUpdate, JBBotConfig, JBBotActivate, JBBotCode
from lib import JBBot


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
    bot_list = [
        {
            "id": "bot1",
            "name": "Test Bot 1",
            "phone_number": "1234567890",
            "status": "active",
            "config_env": {"existing_key": "existing_value"},
            "version": "1.0.0",
            "channels": ["whatsapp"],
            "dsl": "some_dsl",
            "code": "print('Hello World')",
            "requirements": "",
            "created_at": "2022-01-01T00:00:00Z",
            "updated_at": "2022-01-01T00:00:00Z"
        },
        {
            "id": "bot2",
            "name": "Test Bot 2",
            "phone_number": "0987654321",
            "status": "inactive",
            "config_env": {"another_key": "another_value"},
            "version": "1.1.0",
            "channels": ["telegram"],
            "dsl": "some_other_dsl",
            "code": "print('Hello Universe')",
            "requirements": "",
            "created_at": "2022-01-02T00:00:00Z",
            "updated_at": "2022-01-02T00:00:00Z"
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
    bot_id = "bot1"
    update_fields = JBBotUpdate(config_env={"key": "value"})

    # Define the mock JBBot object
    mock_bot = MagicMock(
        id=bot_id,
        name="Test Bot",
        phone_number="1234567890",
        status="inactive",
        config_env={"existing_key": "existing_value"},
        version="1.0.0",
        channels=["whatsapp"],
        required_credentials=[],
        credentials={},
        dsl="some_dsl",
        code="print('Hello World')",
        requirements="",
        created_at="2022-01-01T00:00:00Z",
        updated_at="2022-01-01T00:00:00Z"
    )
    
    mock_get_bot_by_id = AsyncMock(return_value=mock_bot)
    mock_update_bot = AsyncMock()

    with patch("app.main.get_bot_by_id", mock_get_bot_by_id):
        with patch("app.main.update_bot", mock_update_bot):
            response = await client.patch(f"/bot/{bot_id}", json=update_fields.dict(exclude_unset=True))
            
            assert response.status_code == 200
            
            expected_updated_data = {
                "config_env": {
                    "key": encrypt_text("value")
                }
            }
            mock_update_bot.assert_called_once_with(bot_id, expected_updated_data)
            
            returned_bot = response.json()
            assert returned_bot["id"] == bot_id
            assert "config_env" in returned_bot

@pytest.mark.asyncio
async def test_install_bot(client):
    bot_id = "bot1"

    install_content = {
        "name": "Test Bot",
        "status": "inactive",
        "dsl": "some_dsl",
        "code": "print('Hello World')",
        "requirements": "",
        "index_urls": [],
        "version": "1.0.0",
        "required_credentials": []
    }
    
    # Correct mock_bot object structure
    mock_bot = MagicMock(
        id=bot_id,
        name=install_content["name"],
        status=install_content["status"],
        dsl=install_content["dsl"],
        code=install_content["code"],
        requirements=install_content["requirements"],
        index_urls=install_content["index_urls"],
        config_env={},
        required_credentials=install_content["required_credentials"],
        credentials={},
        version=install_content["version"],
        channels={},
        created_at="2022-01-01T00:00:00Z",
        updated_at="2022-01-01T00:00:00Z"
    )

    mock_create_bot = AsyncMock(return_value=mock_bot)

    with patch("app.main.create_bot", mock_create_bot):
        with patch("app.main.produce_message", AsyncMock()) as mock_produce_message:
            response = await client.post("/bot/install", json=install_content)
            assert response.status_code == 200
            mock_create_bot.assert_called_once()
            mock_produce_message.assert_called_once()
            assert response.json() == {"status": "success"}

@pytest.mark.asyncio
async def test_activate_bot(client):
    bot_id = "bot1"
    activate_content = {
        "phone_number": "1234567890",
        "channels": {"whatsapp": "wa_credentials"}
    }

    # Define the mock JBBot object
    mock_bot = MagicMock(
        id=bot_id,
        name="Test Bot",
        status="inactive",
        phone_number=None,
        channels=None,
        required_credentials=[],
        credentials={},
        config_env={"key": "value"},
        version="0.0.1",
        created_at="2022-01-01T00:00:00Z",
        updated_at="2022-01-01T00:00:00Z"
    )

    mock_get_bot_by_id = AsyncMock(return_value=mock_bot)
    mock_get_bot_by_phone_number = AsyncMock(return_value=None)
    mock_update_bot = AsyncMock()

    with patch("app.main.get_bot_by_id", mock_get_bot_by_id):
        with patch("app.main.get_bot_by_phone_number", mock_get_bot_by_phone_number):
            with patch("app.main.update_bot", mock_update_bot):
                response = await client.post(f"/bot/{bot_id}/activate", json=activate_content)
                
                assert response.status_code == 200
                assert response.json() == {"status": "success"}
                
                expected_channels = encrypt_dict({"whatsapp": "wa_credentials"})
                
                mock_update_bot.assert_called_once_with(bot_id, {
                    "phone_number": "1234567890",
                    "channels": expected_channels,
                    "status": "active"
                })

@pytest.mark.asyncio
async def test_deactivate_bot(client):
    bot_id = "bot1"
    
    mock_bot = MagicMock(
        id=bot_id,
        name="Test Bot",
        status="active",
        phone_number="1234567890",
        channels={"whatsapp": "wa_credentials"},
        config_env={"key": "value"},
        credentials={"API_KEY": "secret"},
        version="0.0.1",
        created_at="2022-01-01T00:00:00Z",
        updated_at="2022-01-01T00:00:00Z"
    )
    
    mock_get_bot_by_id = AsyncMock(return_value=mock_bot)
    mock_update_bot = AsyncMock()

    with patch("app.main.get_bot_by_id", mock_get_bot_by_id):
        with patch("app.main.update_bot", mock_update_bot):
            response = await client.get(f"/bot/{bot_id}/deactivate")
            
            assert response.status_code == 200
            
            expected_bot_data = {
                "status": "inactive",
                "phone_number": None,
                "channels": None
            }
            mock_update_bot.assert_called_once_with(bot_id, expected_bot_data)
            
            mock_get_bot_by_id.assert_called_once_with(bot_id)
            
            returned_bot = response.json()
            assert returned_bot["id"] == bot_id
            assert returned_bot["status"] == "inactive"

@pytest.mark.asyncio
async def test_delete_bot(client):
    bot_id = "bot1"

    # Define the mock JBBot object
    mock_bot = MagicMock(
        id=bot_id,
        name="Test Bot",
        status="active",
        phone_number="1234567890",
        channels={"whatsapp": "wa_credentials"},
        config_env={"key": "value"},
        credentials={"API_KEY": "secret"},
        version="0.0.1",
        created_at="2022-01-01T00:00:00Z",
        updated_at="2022-01-01T00:00:00Z"
    )

    mock_get_bot_by_id = AsyncMock(return_value=mock_bot)
    mock_update_bot = AsyncMock()

    with patch("app.main.get_bot_by_id", mock_get_bot_by_id):
        with patch("app.main.update_bot", mock_update_bot):
            response = await client.delete(f"/bot/{bot_id}")
            
            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            
            expected_bot_data = {
                "status": "deleted",
                "phone_number": None,
                "channels": None
            }
            mock_update_bot.assert_called_once_with(bot_id, expected_bot_data)

@pytest.mark.asyncio
async def test_add_bot_configuration(client):
    bot_id = "bot1"
    configuration_content = {
        "credentials": {"key": "value"},
        "config_env": {"key": "value"}
    }

    mock_bot = MagicMock(
        id=bot_id,
        name="Test Bot",
        status="active",
        phone_number="1234567890",
        channels={"whatsapp": "wa_credentials"},
        credentials={},
        config_env={}
    )
    
    mock_get_bot_by_id = AsyncMock(return_value=mock_bot)
    mock_update_bot = AsyncMock()

    with patch("app.main.get_bot_by_id", mock_get_bot_by_id):
        with patch("app.main.update_bot", mock_update_bot):
            response = await client.post(f"/bot/{bot_id}/configure", json=configuration_content)
            
            assert response.status_code == 200
            assert response.json() == {"status": "success"}
            
            expected_credentials = {
                "key": encrypt_text("value")
            }
            expected_bot_data = {
                "credentials": expected_credentials,
                "config_env": {"key": "value"}
            }
            mock_update_bot.assert_called_once_with(bot_id, expected_bot_data)