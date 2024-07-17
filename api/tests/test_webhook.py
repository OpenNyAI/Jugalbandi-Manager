import json
from unittest.mock import patch, MagicMock
import pytest

from lib.data_models import Flow, FlowIntent, CallbackType

from app.handlers.v1 import handle_webhook


# Test cases
@pytest.mark.asyncio
async def test_handle_webhook_valid_data():
    webhook_data = json.dumps({"plugin_uuid": "jbkeyvalid_uuidjbkey", "data": "test"})

    # Mocking the extract_reference_id function
    with patch(
        "app.handlers.v1.get_plugin_reference",
        return_value=MagicMock(session_id="1234", turn_id="5678"),
    ):
        flow_input_generator = handle_webhook(webhook_data)
        flow_input: Flow = await anext(flow_input_generator)

    assert flow_input.source == "api"
    assert flow_input.intent == FlowIntent.CALLBACK
    assert flow_input.callback is not None
    assert flow_input.callback.turn_id == "5678"
    assert flow_input.callback.callback_type == CallbackType.EXTERNAL
    assert flow_input.callback.external == webhook_data


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
