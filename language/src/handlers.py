"""
Handlers for Language Input and Output
"""

import logging
import uuid
from .extension import speech_processor, storage, translator
from lib.audio_converter import convert_to_wav_with_ffmpeg
from lib.data_models import (
    BotOutput,
    ChannelInput,
    ChannelIntent,
    FlowInput,
    LanguageInput,
    LanguageIntent,
    MessageType,
    MessageData,
)
from lib.model import Language


logger = logging.getLogger("language")
logger.setLevel(logging.INFO)


async def handle_input(
    preferred_language: Language, language_input: LanguageInput
) -> str:
    """Handler for Language Input"""
    message_text = language_input.data.message_data.message_text
    english_text = None
    if language_input.data.message_type == MessageType.TEXT:
        logger.info(
            "Received %s text message %s", preferred_language.name, message_text
        )
        vernacular_text = message_text
        english_text = await translator.translate_text(
            vernacular_text,
            preferred_language,
            Language.EN,
        )
    elif language_input.data.message_type == MessageType.AUDIO:
        audio_url = language_input.data.message_data.media_url
        wav_data = await convert_to_wav_with_ffmpeg(audio_url)
        vernacular_text = await speech_processor.speech_to_text(
            wav_data, preferred_language
        )
        logger.info("Vernacular Text %s", vernacular_text)
        english_text = await translator.translate_text(
            vernacular_text,
            preferred_language,
            Language.EN,
        )
        logger.info("English Text %s", english_text)
    elif language_input.data.message_type == MessageType.INTERACTIVE:
        english_text = language_input.data.message_data.message_text

    flow_input = FlowInput(
        source="language",
        intent=LanguageIntent.LANGUAGE_IN,
        session_id=language_input.session_id,
        message_id=language_input.message_id,
        turn_id=language_input.turn_id,
        message_text=english_text,
    )
    return flow_input


async def handle_output(
    preferred_language: Language,
    language_input: LanguageInput,
    turn_type: MessageType,
):
    logger.info("Preferred Language %s", preferred_language)
    logger.info("Language Input %s", language_input)
    logger.info("Turn Type %s", turn_type)
    turn_type = MessageType.__members__.get(turn_type.upper(), MessageType.TEXT)

    media_output_url = None
    channel_inputs = []
    if language_input.data.message_type == MessageType.TEXT:
        # if turn_type == MessageType.AUDIO:
        logger.info("Turn Type == AUDIO")
        vernacular_text = await translator.translate_text(
            language_input.data.message_data.message_text,
            Language.EN,
            preferred_language,
        )
        logger.info("Vernacular Text %s", vernacular_text)
        try:
            audio_content = await speech_processor.text_to_speech(
                vernacular_text, preferred_language
            )
            fid = str(uuid.uuid4())
            filename = f"{fid}.mp3"
            await storage.write_file(filename, audio_content, "audio/mpeg")
            media_output_url = await storage.make_public(filename)
        except Exception as e:
            logger.error("Error in text to speech: %s", e)
        return [
            ChannelInput(
                source="language",
                intent=ChannelIntent.BOT_OUT,
                session_id=language_input.session_id,
                message_id=fid,
                turn_id=language_input.turn_id,
                data=BotOutput(
                    message_type=MessageType.AUDIO,
                    message_data=MessageData(
                        message_text=None, media_url=media_output_url
                    ),
                ),
            ),
            ChannelInput(
                source="language",
                intent=ChannelIntent.BOT_OUT,
                session_id=language_input.session_id,
                message_id=str(uuid.uuid4()),
                turn_id=language_input.turn_id,
                data=BotOutput(
                    message_type=MessageType.TEXT,
                    message_data=MessageData(
                        message_text=vernacular_text, media_url=None
                    ),
                    options_list=language_input.data.options_list,
                    menu_selector=language_input.data.menu_selector,
                    menu_title=language_input.data.menu_title,
                    header=language_input.data.header,
                    footer=language_input.data.footer,
                ),
            ),
        ]
        # else:
        #     # Turn Type == TEXT | DOCUMENT | INTERACTIVE | IMAGE
        #     vernacular_text = await translator.translate_text(
        #         language_input.message_data.message_text,
        #         Language.EN,
        #         preferred_language,
        #     )
        #     logger.info("Vernacular Text %s", vernacular_text)

    elif language_input.data.message_type == MessageType.DOCUMENT:
        vernacular_text = await translator.translate_text(
            language_input.data.message_data.message_text,
            Language.EN,
            preferred_language,
        )
        media_output_url = language_input.data.message_data.media_url
    elif language_input.data.message_type == MessageType.IMAGE:
        vernacular_text = await translator.translate_text(
            language_input.data.message_data.message_text,
            Language.EN,
            preferred_language,
        )
        media_output_url = language_input.data.message_data.media_url
    elif language_input.data.message_type == MessageType.INTERACTIVE:
        vernacular_text = await translator.translate_text(
            language_input.data.message_data.message_text,
            Language.EN,
            preferred_language,
        )
        if language_input.data.header:
            language_input.data.header = await translator.translate_text(
                language_input.data.header, Language.EN, preferred_language
            )
        if language_input.data.footer:
            language_input.data.footer = await translator.translate_text(
                language_input.data.footer, Language.EN, preferred_language
            )
        
        for option in language_input.data.options_list:
            option.title = await translator.translate_text(
                option.title, Language.EN, preferred_language
            )
        try:
            audio_content = await speech_processor.text_to_speech(
                vernacular_text, preferred_language
            )
            fid = str(uuid.uuid4())
            filename = f"{fid}.mp3"
            await storage.write_file(filename, audio_content, "audio/mpeg")
            audio_url = await storage.make_public(filename)
            channel_inputs.append(
                ChannelInput(
                    source="language",
                    intent=ChannelIntent.BOT_OUT,
                    session_id=language_input.session_id,
                    message_id=fid,
                    turn_id=language_input.turn_id,
                    data=BotOutput(
                        message_type=MessageType.AUDIO,
                        message_data=MessageData(
                            message_text=None, media_url=audio_url
                        ),
                    ),
                )
            )
        except Exception as e:
            logger.error("Error in text to speech: %s", e)

    channel_input = ChannelInput(
        source="language",
        intent=ChannelIntent.BOT_OUT,
        session_id=language_input.session_id,
        message_id=str(uuid.uuid4()),
        turn_id=language_input.turn_id,
        data=BotOutput(
            message_type=language_input.data.message_type,
            message_data=MessageData(
                message_text=vernacular_text, media_url=media_output_url
            ),
            options_list=language_input.data.options_list,
            menu_selector=language_input.data.menu_selector,
            menu_title=language_input.data.menu_title,
            header=language_input.data.header,
            footer=language_input.data.footer,
        ),
    )

    channel_inputs.append(channel_input)
    return channel_inputs
