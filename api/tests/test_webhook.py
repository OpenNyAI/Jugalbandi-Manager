import json
from unittest.mock import patch, MagicMock
import pytest

from app.handlers import handle_webhook


# Test cases
@pytest.mark.asyncio
async def test_handle_webhook_valid_data():
    webhook_data = json.dumps({"plugin_uuid": "jbkeyvalid_uuidjbkey", "data": "test"})

    # Mocking the extract_reference_id function
    with patch(
        "app.handlers.get_plugin_reference",
        return_value=MagicMock(session_id="1234", turn_id="5678"),
    ):
        flow_input_generator = handle_webhook(webhook_data)
        flow_input = await anext(flow_input_generator)

    assert flow_input.source == "api"
    assert flow_input.session_id == "1234"
    assert flow_input.turn_id == "5678"
    assert flow_input.plugin_input == json.loads(webhook_data)


@pytest.mark.asyncio
async def test_handle_webhook_invalid_data():
    webhook_data = json.dumps({"data": "test"})

    with pytest.raises(ValueError, match="Plugin UUID not found in webhook data"):
        flow_input_generator = handle_webhook(webhook_data)
        await anext(flow_input_generator)


@pytest.mark.asyncio
async def test_handle_webhook_empty_data():
    webhook_data = ""

    with pytest.raises(ValueError, match="Plugin UUID not found in webhook data"):
        flow_input_generator = handle_webhook(webhook_data)
        await anext(flow_input_generator)
