"""
Handlers for Language Input and Output
"""

import traceback
from typing import List
import logging
import uuid
from .extension import speech_processor, storage, translator
from lib.audio_converter import convert_to_wav_with_ffmpeg
from lib.data_models import (
    Channel,
    ChannelIntent,
    Flow,
    FlowIntent,
    UserInput,
    MessageType,
    Message,
    TextMessage,
    AudioMessage,
    DocumentMessage,
    ImageMessage,
    ButtonMessage,
    Option,
    ListMessage,
)
from lib.model import LanguageCodes


logger = logging.getLogger("language")
logger.setLevel(logging.INFO)


async def handle_input(
    turn_id: str, preferred_language: LanguageCodes, message: Message
) -> Flow:
    """Handler for Language Input"""
    english_text = None
    if message.message_type == MessageType.TEXT:
        if not message.text:
            raise ValueError("Message text is empty")
        message_text = message.text.body
        logger.info(
            "Received %s text message %s", preferred_language.name, message_text
        )
        vernacular_text = message_text
        english_text = await translator.translate_text(
            vernacular_text,
            preferred_language,
            LanguageCodes.EN,
        )
        text_message = TextMessage(body=english_text)
        message = Message(
            message_type=MessageType.TEXT,
            text=text_message,
        )
    elif message.message_type == MessageType.AUDIO:
        if not message.audio:
            raise ValueError("Message audio is empty")
        audio_url = message.audio.media_url
        wav_data = await convert_to_wav_with_ffmpeg(audio_url)
        vernacular_text = await speech_processor.speech_to_text(
            wav_data, preferred_language
        )
        logger.info("Vernacular Text %s", vernacular_text)
        english_text = await translator.translate_text(
            vernacular_text,
            preferred_language,
            LanguageCodes.EN,
        )
        logger.info("English Text %s", english_text)
        text_message = TextMessage(body=english_text)
        message = Message(
            message_type=MessageType.TEXT,
            text=text_message,
        )

    flow_input = Flow(
        source="language",
        intent=FlowIntent.USER_INPUT,
        user_input=UserInput(turn_id=turn_id, message=message),
    )
    return flow_input


async def handle_output(
    turn_id: str, preferred_language: LanguageCodes, message: Message
) -> List[Channel]:
    logger.info("Preferred Language %s", preferred_language)
    logger.info("Message %s", message)

    media_output_url = None
    channel_inputs = []
    message_type = message.message_type
    if message_type == MessageType.TEXT:
        if not message.text:
            raise ValueError("Message text is empty")

        vernacular_body = await translator.translate_text(
            message.text.body,
            LanguageCodes.EN,
            preferred_language,
        )
        translated_text_message = TextMessage(body=vernacular_body)
        if message.text.header:
            translated_text_message.header = await translator.translate_text(
                message.text.header, LanguageCodes.EN, preferred_language
            )
        if message.text.footer:
            translated_text_message.footer = await translator.translate_text(
                message.text.footer, LanguageCodes.EN, preferred_language
            )
        logger.info("Vernacular Text %s", vernacular_body)
        channel_inputs.append(
            Channel(
                source="language",
                intent=ChannelIntent.CHANNEL_OUT,
                turn_id=turn_id,
                bot_output=Message(
                    message_type=MessageType.TEXT, text=translated_text_message
                ),
            )
        )
        try:
            audio_content = await speech_processor.text_to_speech(
                vernacular_body, preferred_language
            )
            fid = str(uuid.uuid4())
            filename = f"{fid}.mp3"
            await storage.write_file(filename, audio_content, "audio/mpeg")
            media_output_url = await storage.public_url(filename)
            translated_audio_message = AudioMessage(media_url=media_output_url)
            channel_inputs.append(
                Channel(
                    source="language",
                    intent=ChannelIntent.CHANNEL_OUT,
                    turn_id=turn_id,
                    bot_output=Message(
                        message_type=MessageType.AUDIO, audio=translated_audio_message
                    ),
                )
            )
        except Exception as e:
            logger.error("Error in text to speech: %s", e)

    elif message_type == MessageType.DOCUMENT:
        if not message.document:
            raise ValueError("Message document is empty")
        vernacular_text = await translator.translate_text(
            message.document.caption,
            LanguageCodes.EN,
            preferred_language,
        )
        translated_document_message = DocumentMessage(
            url=message.document.url,
            caption=vernacular_text,
            name=message.document.name,
        )
        channel_inputs.append(
            Channel(
                source="language",
                intent=ChannelIntent.CHANNEL_OUT,
                turn_id=turn_id,
                bot_output=Message(
                    message_type=MessageType.DOCUMENT,
                    document=translated_document_message,
                ),
            )
        )
    elif message_type == MessageType.IMAGE:
        if not message.image:
            raise ValueError("Message image is empty")
        vernacular_text = await translator.translate_text(
            message.image.caption,
            LanguageCodes.EN,
            preferred_language,
        )
        translated_image_message = ImageMessage(
            url=message.image.url,
            caption=vernacular_text,
        )
        channel_inputs.append(
            Channel(
                source="language",
                intent=ChannelIntent.CHANNEL_OUT,
                turn_id=turn_id,
                bot_output=Message(
                    message_type=MessageType.IMAGE, image=translated_image_message
                ),
            )
        )
    elif message_type == MessageType.BUTTON or message_type == MessageType.OPTION_LIST:
        if message_type == MessageType.BUTTON:
            interactive_message = message.button
        elif message_type == MessageType.OPTION_LIST:
            interactive_message = message.option_list

        if not interactive_message:
            raise ValueError("Interactive message is empty")
        vernacular_body = await translator.translate_text(
            interactive_message.body,
            LanguageCodes.EN,
            preferred_language,
        )
        vernacular_options = [
            Option(
                option_id=option.option_id,
                option_text=await translator.translate_text(
                    option.option_text, LanguageCodes.EN, preferred_language
                ),
            )
            for option in interactive_message.options
        ]
        vernacular_header = await translator.translate_text(
            interactive_message.header, LanguageCodes.EN, preferred_language
        )
        vernacular_footer = await translator.translate_text(
            interactive_message.footer, LanguageCodes.EN, preferred_language
        )
        if message_type == MessageType.BUTTON:
            translated_interactive_message = ButtonMessage(
                body=vernacular_body,
                header=vernacular_header,
                footer=vernacular_footer,
                options=vernacular_options,
            )
            channel_input = Channel(
                source="language",
                intent=ChannelIntent.CHANNEL_OUT,
                turn_id=turn_id,
                bot_output=Message(
                    message_type=MessageType.BUTTON,
                    button=translated_interactive_message,
                ),
            )
        else:
            translated_interactive_message = ListMessage(
                body=vernacular_body,
                header=vernacular_header,
                footer=vernacular_footer,
                options=vernacular_options,
                button_text=await translator.translate_text(
                    interactive_message.button_text,
                    LanguageCodes.EN,
                    preferred_language,
                ),
                list_title=await translator.translate_text(
                    interactive_message.list_title, LanguageCodes.EN, preferred_language
                ),
            )
            channel_input = Channel(
                source="language",
                intent=ChannelIntent.CHANNEL_OUT,
                turn_id=turn_id,
                bot_output=Message(
                    message_type=MessageType.OPTION_LIST,
                    option_list=translated_interactive_message,
                ),
            )
        channel_inputs.append(channel_input)
        try:
            audio_content = await speech_processor.text_to_speech(
                vernacular_body, preferred_language
            )
            fid = str(uuid.uuid4())
            filename = f"{fid}.mp3"
            await storage.write_file(filename, audio_content, "audio/mpeg")
            audio_url = await storage.public_url(filename)
            channel_inputs.append(
                Channel(
                    source="language",
                    intent=ChannelIntent.CHANNEL_OUT,
                    turn_id=turn_id,
                    bot_output=Message(
                        message_type=MessageType.AUDIO,
                        audio=AudioMessage(media_url=audio_url),
                    ),
                )
            )
        except Exception as e:
            logger.error("Error in text to speech: %s %s", e, traceback.format_exc())

    return channel_inputs
