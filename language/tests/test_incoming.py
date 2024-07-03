from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from lib.data_models import (
    LanguageInput,
    MessageType,
    LanguageIntent,
    FlowInput,
    BotInput,
    MessageData,
)
from lib.model import Language

mock_storage_instance = MagicMock()
mock_write_file = AsyncMock()
mock_public_url = AsyncMock(return_value="https://storage.url/test_audio.ogg")
mock_storage_instance.write_file = mock_write_file
mock_storage_instance.public_url = mock_public_url

mock_translator_instance = MagicMock()
mock_translate_text = AsyncMock()
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

        handle_input = src.handlers.handle_input


# Sample inputs for different message types
text_message = "Hello, this is a text message."
audio_url = "http://example.com/audio.mp3"
interactive_message = "This is an interactive message."


@pytest.mark.asyncio
async def test_handle_input_text_message():
    mock_extension.reset_mock()

    preferred_language = Language.EN
    language_input = LanguageInput(
        session_id="session1",
        message_id="msg1",
        turn_id="turn1",
        source="channel",
        intent=LanguageIntent.LANGUAGE_IN,
        data=BotInput(
            message_type=MessageType.TEXT,
            message_data=MessageData(message_text=text_message),
        ),
    )
    mock_translate_text.return_value = "Translated text message"

    result = await handle_input(preferred_language, language_input)
    print(result)

    # Verifying the results
    mock_translate_text.assert_called_once_with(
        text_message, preferred_language, Language.EN
    )
    assert result.message_text == "Translated text message"
    assert isinstance(result, FlowInput)
    assert result.intent == LanguageIntent.LANGUAGE_IN
    assert result.session_id == "session1"
    assert result.message_id == "msg1"
    assert result.turn_id == "turn1"


@pytest.mark.asyncio
async def test_handle_input_audio_message():
    mock_extension.reset_mock()

    # Setting up the mocks
    preferred_language = Language.EN  # Example language
    language_input = LanguageInput(
        session_id="session2",
        message_id="msg2",
        turn_id="turn2",
        source="channel",
        intent=LanguageIntent.LANGUAGE_IN,
        data=BotInput(
            message_type=MessageType.AUDIO,
            message_data=MessageData(media_url=audio_url),
        ),
    )

    mock_speech_to_text.return_value = "Vernacular text"
    mock_translate_text.return_value = "Translated audio message"

    result = await handle_input(preferred_language, language_input)

    # Verifying the results
    mock_convert_to_wav.assert_called_once_with(audio_url)
    mock_speech_to_text.assert_called_once_with(b"wav_data", preferred_language)
    mock_translate_text.assert_called_once_with(
        "Vernacular text", preferred_language, Language.EN
    )
    assert result.message_text == "Translated audio message"
    assert isinstance(result, FlowInput)
    assert result.intent == LanguageIntent.LANGUAGE_IN
    assert result.session_id == "session2"
    assert result.message_id == "msg2"
    assert result.turn_id == "turn2"


@pytest.mark.asyncio
async def test_handle_input_interactive_message():
    mock_extension.reset_mock()

    # Setting up the mocks
    preferred_language = Language.EN  # Example language
    language_input = LanguageInput(
        session_id="session3",
        message_id="msg3",
        turn_id="turn3",
        source="channel",
        intent=LanguageIntent.LANGUAGE_IN,
        data=BotInput(
            message_type=MessageType.INTERACTIVE,
            message_data=MessageData(message_text=interactive_message),
        ),
    )

    result = await handle_input(preferred_language, language_input)

    # Verifying the results
    assert result.message_text == interactive_message
    assert isinstance(result, FlowInput)
    assert result.intent == LanguageIntent.LANGUAGE_IN
    assert result.session_id == "session3"
    assert result.message_id == "msg3"
    assert result.turn_id == "turn3"
