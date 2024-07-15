from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from lib.data_models import BotConfig, Flow, Bot, FlowIntent, BotIntent

mock_extension = MagicMock()


@pytest.mark.asyncio
@patch.dict("sys.modules", {"src.extensions": mock_extension})
@patch("src.handlers.bot_install.create_bot", return_value=AsyncMock())
@patch("src.handlers.bot_install.install_bot", return_value=AsyncMock())
async def test_handle_bot_install_with_valid_bot_config(
    mock_install_bot, mock_create_bot
):
    flow_input = Flow(
        source="api",
        intent=FlowIntent.BOT,
        bot_config=BotConfig(
            bot_id="test_bot_id",
            intent=BotIntent.INSTALL,
            bot=Bot(
                name="test_bot_name",
                fsm_code="test_bot_fsm_code",
                requirements_txt="test_bot_requirements_txt",
                index_urls=["test_index_urls"],
                required_credentials=["API_KEY"],
                version="0.0.1",
            ),
        ),
    )

    from src.handlers.flow_input import handle_flow_input

    await handle_flow_input(flow_input)

    mock_install_bot.assert_awaited_once_with(
        bot_id="test_bot_id",
        bot_fsm_code="test_bot_fsm_code",
        bot_requirements_txt="test_bot_requirements_txt",
        index_urls=["test_index_urls"],
    )
    mock_create_bot.assert_awaited_once_with(
        bot_id="test_bot_id",
        name="test_bot_name",
        code="test_bot_fsm_code",
        requirements="test_bot_requirements_txt",
        index_urls=["test_index_urls"],
        required_credentials=["API_KEY"],
        version="0.0.1",
    )


@pytest.mark.asyncio
@patch.dict("sys.modules", {"src.extensions": mock_extension})
@patch("src.handlers.bot_install.delete_bot", return_value=AsyncMock())
async def test_handle_bot_delete(mock_delete_bot):
    flow_input = Flow(
        source="some_invalid_source",
        intent=FlowIntent.BOT,
        bot_config=BotConfig(
            bot_id="test_bot_id",
            intent=BotIntent.DELETE,
        ),
    )
    from src.handlers.flow_input import handle_flow_input

    await handle_flow_input(flow_input)

    mock_delete_bot.assert_awaited_once_with("test_bot_id")
