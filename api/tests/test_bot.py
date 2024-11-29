from unittest.mock import patch
import pytest
from lib.data_models import Flow, BotConfig, BotIntent, FlowIntent, Bot
from lib.models import JBBot
from app.handlers.v2.bot import list_bots, install
from app.jb_schema import JBBotCode

@pytest.mark.asyncio
async def test_list_bots():
    mock_bot1 = JBBot(id="test_bot_1", name="Bot1", status="active")
    mock_bot2 = JBBot(id="test_bot_2", name="Bot2", status="active")

    bot_list = [mock_bot1,mock_bot2]
    with patch("app.handlers.v2.bot.get_bot_list", return_value = bot_list) as mock_get_bot_list:
        result = await list_bots()

        assert result == bot_list
        mock_get_bot_list.assert_awaited_once()

@pytest.mark.asyncio
async def test_install():

    mock_jbbot_code = JBBotCode(
        name = "Bot1",
        status = "active",
        dsl = "test_dsl",
        code = "test_code",
        requirements = "codaio",
        index_urls = ["index_url_1","index_url_2"],
        version = "1.0.0",
    )

    mock_bot1 = JBBot(id="test_bot_1", 
                      name=mock_jbbot_code.name, 
                      status=mock_jbbot_code.status,
                      dsl = mock_jbbot_code.dsl, 
                      code = mock_jbbot_code.code, 
                      requirements = mock_jbbot_code.requirements, 
                      index_urls = mock_jbbot_code.index_urls, 
                      version = mock_jbbot_code.version)

    with patch("app.handlers.v2.bot.create_bot", return_value = mock_bot1) as mock_create_bot:
        result = await install(mock_jbbot_code)

        assert isinstance(result,Flow)
        assert result.source == "api"
        assert result.intent == FlowIntent.BOT
        assert isinstance(result.bot_config,BotConfig)
        assert result.bot_config.bot_id == mock_bot1.id
        assert isinstance(result.bot_config.bot,Bot)
        assert result.bot_config.bot.name == mock_jbbot_code.name
        assert result.bot_config.bot.fsm_code == mock_jbbot_code.code
        assert result.bot_config.bot.requirements_txt == mock_jbbot_code.requirements
        assert result.bot_config.bot.index_urls == mock_jbbot_code.index_urls
        assert result.bot_config.bot.version == mock_bot1.version
        
        mock_create_bot.assert_awaited_once_with(mock_jbbot_code.model_dump())
