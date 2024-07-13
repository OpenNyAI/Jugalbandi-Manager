from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from lib.data_models import BotConfig, FlowInput
from lib.models import JBBot

mock_extension = MagicMock()
with patch.dict("sys.modules", {"src.extensions": mock_extension}):
    from src.handlers.flow_input import handle_flow_input


@pytest.mark.asyncio
async def test_handle_flow_input_with_valid_bot_config():
    bot_config = BotConfig(
        bot_id="test_bot_id",
        bot_name="test_bot_name",
        bot_fsm_code="test_bot_fsm_code",
        bot_requirements_txt="test_bot_requirements_txt",
        bot_config_env={"test_key": "test_value"},
        index_urls=["test_index_urls"],
    )
    flow_input = FlowInput(source="api", bot_config=bot_config)

    mock_install_or_update_bot = AsyncMock()
    mock_create_bot = AsyncMock(
        return_value=JBBot(
            id="test_bot_id",
            name="test_bot_name",
            code="test_bot_fsm_code",
            requirements="test_bot_requirements_txt",
            config_env={"test_key": "test_value"},
            index_urls=["test_index_urls"],
        )
    )

    with patch.dict("sys.modules", {"src.extensions": mock_extension}):
        with patch(
            "src.handlers.bot_install.install_or_update_bot", mock_install_or_update_bot
        ) as mock_install:
            with patch(
                "src.handlers.bot_install.create_bot", mock_create_bot
            ) as mock_create:
                from src.handlers.flow_input import handle_flow_input

                result = await handle_flow_input(flow_input)

    mock_install.assert_awaited_once_with(
        bot_id="test_bot_id",
        bot_fsm_code="test_bot_fsm_code",
        bot_requirements_txt="test_bot_requirements_txt",
        index_urls=["test_index_urls"],
    )
    mock_create.assert_awaited_once_with(
        "test_bot_id", flow_input.bot_config.model_dump()
    )


@pytest.mark.asyncio
async def test_handle_flow_input_with_invalid_source():
    bot_config = BotConfig(
        bot_id="test_bot_id",
        bot_name="test_bot_name",
        bot_fsm_code="test_bot_fsm_code",
        bot_requirements_txt="test_bot_requirements_txt",
        bot_config_env={"test_key": "test_value"},
        index_urls=["test_index_urls"],
    )
    flow_input = FlowInput(
        source="other",
        bot_config=bot_config,
    )

    with patch(
        "src.handlers.bot_install.install_or_update_bot", new=AsyncMock()
    ) as mock_install, patch(
        "src.handlers.bot_install.create_bot", new=AsyncMock()
    ) as mock_create:

        with pytest.raises(ValueError, match="Invalid source in flow input"):
            await handle_flow_input(flow_input)


@pytest.mark.asyncio
async def test_handle_flow_input_with_bot_config_missing_fsm_code():
    bot_config = BotConfig(
        bot_id="test_bot_id",
        bot_name="test_bot_name",
        bot_requirements_txt="test_bot_requirements_txt",
        bot_config_env={"test_key": "test_value"},
        index_urls=["test_index_urls"],
    )
    flow_input = FlowInput(source="api", bot_config=bot_config)

    with patch(
        "src.handlers.bot_install.install_or_update_bot", new=AsyncMock()
    ) as mock_install, patch(
        "src.handlers.bot_install.create_bot", new=AsyncMock()
    ) as mock_create:

        with pytest.raises(ValueError, match="FSM code is required"):
            await handle_flow_input(flow_input)

        mock_install.assert_not_awaited()
        mock_create.assert_not_awaited()
