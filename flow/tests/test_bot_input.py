from itertools import product
from unittest.mock import MagicMock, patch, AsyncMock
import json
import pytest
from lib.models import JBBot
from lib.data_models import (
    FlowInput,
    LanguageIntent,
    FSMOutput,
    MessageType,
    LanguageInput,
    BotOutput,
    MessageData,
    OptionsListType,
    ChannelInput,
    ChannelIntent,
    RAGInput,
    RAGResponse,
)

mock_bot = JBBot(
    id="test_bot_id",
    name="test_bot_name",
    status="active",
    dsl="",
    code="test_code",
    requirements="test_requirements",
    index_urls=["test_index_urls"],
    config_env={"API_SECRET": "test_api_secret"},
    required_credentials=["API_KEY", "API_SECRET"],
    credentials={
        "API_KEY": "test_api_key",
        "API_SECRET": "test_api_secret",
    },
    version="0.0.1",
)


flow_inputs = {
    "language": FlowInput(
        source="language",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id="test_session_id",
        message_id="test_message_id",
        turn_id="test_turn_id",
        message_text="test_message_text",
    ),
    "api": FlowInput(
        source="api",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id="test_session_id",
        message_id="test_message_id",
        turn_id="test_turn_id",
        plugin_input={"test_plugin_key": "test_plugin_value"},
    ),
    "retriever": FlowInput(
        source="retriever",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id="test_session_id",
        message_id="test_message_id",
        turn_id="test_turn_id",
        rag_response=[
            RAGResponse(chunk="test_chunk_text_1"),
            RAGResponse(chunk="test_chunk_text_2"),
        ],
    ),
    "channel_msg": FlowInput(
        source="channel",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id="test_session_id",
        message_id="test_message_id",
        turn_id="test_turn_id",
        message_text="test_message_text",
    ),
    "channel_form": FlowInput(
        source="channel",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id="test_session_id",
        message_id="test_message_id",
        turn_id="test_turn_id",
        form_response={"test_form_key": "test_form_value"},
    ),
    "channel_dialog": FlowInput(
        source="channel",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id="test_session_id",
        message_id="test_message_id",
        turn_id="test_turn_id",
        dialog="test_dialog",
    ),
}

fsm_and_assertions = {
    "out_text": (
        FSMOutput(
            dest="out",
            type=MessageType.TEXT,
            text="test_text",
        ),
        LanguageInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            intent=LanguageIntent.LANGUAGE_OUT,
            data=BotOutput(
                message_type=MessageType.TEXT,
                message_data=MessageData(
                    message_text="test_text",
                    media_url=None,
                ),
            ),
        ),
    ),
    "out_interactive": (
        FSMOutput(
            dest="out",
            type=MessageType.INTERACTIVE,
            text="test_text",
            header="test_header",
            footer="test_footer",
            menu_selector="test_menu_selector",
            menu_title="test_menu_title",
            options_list=[
                OptionsListType(id="test_id_1", title="test_title_1"),
                OptionsListType(id="test_id_2", title="test_title_2"),
            ],
        ),
        LanguageInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            intent=LanguageIntent.LANGUAGE_OUT,
            data=BotOutput(
                message_type=MessageType.INTERACTIVE,
                message_data=MessageData(
                    message_text="test_text",
                    media_url=None,
                ),
                header="test_header",
                footer="test_footer",
                menu_selector="test_menu_selector",
                menu_title="test_menu_title",
                options_list=[
                    OptionsListType(id="test_id_1", title="test_title_1"),
                    OptionsListType(id="test_id_2", title="test_title_2"),
                ],
            ),
        ),
    ),
    "out_image": (
        FSMOutput(
            dest="out",
            type=MessageType.IMAGE,
            media_url="test_media_url",
            text="test_text",
        ),
        LanguageInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            intent=LanguageIntent.LANGUAGE_OUT,
            data=BotOutput(
                message_type=MessageType.IMAGE,
                message_data=MessageData(
                    message_text="test_text",
                    media_url="test_media_url",
                ),
            ),
        ),
    ),
    "out_document": (
        FSMOutput(
            dest="out",
            type=MessageType.DOCUMENT,
            media_url="test_media_url",
            text="test_text",
        ),
        LanguageInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            intent=LanguageIntent.LANGUAGE_OUT,
            data=BotOutput(
                message_type=MessageType.DOCUMENT,
                message_data=MessageData(
                    message_text="test_text",
                    media_url="test_media_url",
                ),
            ),
        ),
    ),
    "out_form": (
        FSMOutput(
            dest="channel",
            type=MessageType.FORM,
            text="test_text",
            form_id="test_form_id",
        ),
        ChannelInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            message_id="test_message_id",
            intent=ChannelIntent.BOT_OUT,
            data=BotOutput(
                message_type=MessageType.FORM,
                message_data=MessageData(message_text="test_text"),
                form_id="test_form_id",
            ),
        ),
    ),
    "out_dialog": (
        FSMOutput(
            dest="channel",
            type=MessageType.DIALOG,
            text="test_text",
            dialog="test_dialog",
        ),
        ChannelInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            message_id="test_message_id",
            intent=ChannelIntent.BOT_OUT,
            data=BotOutput(
                message_type=MessageType.DIALOG,
                message_data=MessageData(message_text="test_text"),
            ),
            dialog="test_dialog",
        ),
    ),
    "out_rag": (
        FSMOutput(
            dest="rag",
            text="test_text",
        ),
        RAGInput(
            source="flow",
            session_id="test_session_id",
            turn_id="test_turn_id",
            collection_name="KB_Law_Files",
            query="test_text",
            top_chunk_k_value=5,
        ),
    ),
}

test_cases = {
    f"{flow_input.source}_{name}_{input_name}": (flow_input, fsm_output, flow_output)
    for (input_name, flow_input), (name, (fsm_output, flow_output)) in product(
        flow_inputs.items(), fsm_and_assertions.items()
    )
}


mock_produce_message = MagicMock()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "flow_input, mock_fsm_output, flow_output",
    list(test_cases.values()),
    ids=list(test_cases.keys()),
)
@patch.dict(
    "sys.modules", {"src.extensions": MagicMock(produce_message=mock_produce_message)}
)
@patch("src.handlers.bot_input.get_state_by_pid", return_value=AsyncMock())
@patch("src.handlers.bot_input.update_state_and_variables", return_value=AsyncMock())
@patch("src.handlers.bot_input.get_bot_by_session_id", return_value=mock_bot)
@patch("src.handlers.bot_input.subprocess.run", return_value=MagicMock())
async def test_handle_flow_input(
    mock_subprocess_run,
    mock_get_bot_by_session_id,
    mock_update_state_and_variables,
    mock_get_state_by_pid,
    flow_input,
    mock_fsm_output,
    flow_output,
):
    mock_produce_message.reset_mock()

    mock_state = MagicMock(variables={"test_key": "test_value"})
    mock_get_state_by_pid.return_value = mock_state
    mock_subprocess_run.return_value = MagicMock(
        stdout=f'{json.dumps({"callback_message": json.loads(mock_fsm_output.model_dump_json())})}\n{json.dumps({"new_state": {"state": "test_state", "variables": {"test_key": "test_value"}}})}',
        stderr=None,
    )

    from src.handlers.flow_input import handle_flow_input

    await handle_flow_input(flow_input)

    mock_produce_message.assert_called_once_with(flow_output)
    mock_update_state_and_variables.assert_called_once_with(
        "test_session_id",
        "zerotwo",
        {"state": "test_state", "variables": {"test_key": "test_value"}},
    )
