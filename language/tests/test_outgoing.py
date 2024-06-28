from unittest import mock
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from lib.data_models import (
    LanguageInput,
    MessageType,
    LanguageIntent,
    BotOutput,
    MessageData,
    OptionsListType,
)
from lib.model import Language

mock_storage_instance = MagicMock()
mock_write_file = AsyncMock()
mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")
mock_storage_instance.write_file = mock_write_file
mock_storage_instance.public_url = mock_public_url

mock_translator_instance = MagicMock()
mock_translate_text = AsyncMock(side_effect=lambda x, y, z: f"translated_{x}")
mock_translator_instance.translate_text = mock_translate_text

mock_speech_processor_instance = MagicMock()
mock_text_to_speech = AsyncMock(return_value=b"wav_data")
mock_speech_processor_instance.text_to_speech = mock_text_to_speech
mock_speech_to_text = AsyncMock(return_value="Vernacular text")
mock_speech_processor_instance.speech_to_text = mock_speech_to_text

mock_extension = MagicMock()
mock_extension.translator = mock_translator_instance
mock_extension.speech_processor = mock_speech_processor_instance
mock_extension.storage = mock_storage_instance

mock_convert_to_wav = AsyncMock(return_value=b"wav_data")

with patch.dict("sys.modules", {"src.extension": mock_extension}):
    with patch("lib.audio_converter.convert_to_wav_with_ffmpeg", mock_convert_to_wav):
        import src.handlers

        handle_output = src.handlers.handle_output


@pytest.mark.asyncio
async def test_handle_output_text_message():
    mock_extension.reset_mock()
    language_input = LanguageInput(
        source="flow",
        intent=LanguageIntent.LANGUAGE_OUT,
        session_id="test_session",
        turn_id="test_turn",
        data=BotOutput(
            message_type=MessageType.TEXT,
            message_data=MessageData(message_text="hello"),
        ),
    )
    result = await handle_output(Language.EN, language_input)
    assert len(result) == 2
    assert result[0].data.message_type == MessageType.AUDIO
    assert result[0].data.message_data.media_url == "https://storage.url/test_audio.ogg"
    assert result[1].data.message_type == MessageType.TEXT
    assert result[1].data.message_data.message_text == "translated_hello"


@pytest.mark.asyncio
async def test_handle_output_document_message():
    mock_extension.reset_mock()
    language_input = LanguageInput(
        source="flow",
        intent=LanguageIntent.LANGUAGE_OUT,
        session_id="test_session",
        turn_id="test_turn",
        data=BotOutput(
            message_type=MessageType.DOCUMENT,
            message_data=MessageData(
                message_text="document text", media_url="http://example.com/doc.pdf"
            ),
        ),
    )
    result = await handle_output(Language.EN, language_input)
    assert len(result) == 1
    assert result[0].data.message_type == MessageType.DOCUMENT
    assert result[0].data.message_data.message_text == "translated_document text"
    assert result[0].data.message_data.media_url == "http://example.com/doc.pdf"


@pytest.mark.asyncio
async def test_handle_output_image_message():
    mock_extension.reset_mock()
    language_input = LanguageInput(
        source="flow",
        intent=LanguageIntent.LANGUAGE_OUT,
        session_id="test_session",
        turn_id="test_turn",
        data=BotOutput(
            message_type=MessageType.IMAGE,
            message_data=MessageData(
                message_text="image text", media_url="http://example.com/image.png"
            ),
        ),
    )
    result = await handle_output(Language.EN, language_input)
    assert len(result) == 1
    assert result[0].data.message_type == MessageType.IMAGE
    assert result[0].data.message_data.message_text == "translated_image text"
    assert result[0].data.message_data.media_url == "http://example.com/image.png"


@pytest.mark.asyncio
async def test_handle_output_interactive_message():
    mock_extension.reset_mock()
    language_input = LanguageInput(
        source="flow",
        intent=LanguageIntent.LANGUAGE_OUT,
        session_id="test_session",
        turn_id="test_turn",
        data=BotOutput(
            message_type=MessageType.INTERACTIVE,
            message_data=MessageData(message_text="interactive text"),
            options_list=[
                OptionsListType(id="1", title="Option 1"),
                OptionsListType(id="2", title="Option 2"),
            ],
            header="header text",
            footer="footer text",
        ),
    )
    result = await handle_output(Language.EN, language_input)
    assert len(result) == 2
    assert result[0].data.message_type == MessageType.AUDIO
    assert result[0].data.message_data.media_url == "https://storage.url/test_audio.ogg"
    assert result[1].data.message_type == MessageType.INTERACTIVE
    assert result[1].data.message_data.message_text == "translated_interactive text"
    assert result[1].data.header == "translated_header text"
    assert result[1].data.footer == "translated_footer text"
    assert result[1].data.options_list[0].title == "translated_Option 1"
    assert result[1].data.options_list[1].title == "translated_Option 2"
