import logging
import uuid
import json
from typing import Dict, AsyncGenerator
from lib.whatsapp import WhatsappHelper
from lib.data_models import (
    ChannelInput,
    ChannelIntent,
    ChannelData,
    BotInput,
    MessageType,
    MessageData,
    FlowInput,
)
from ...crud import (
    get_active_channel_by_identifier,
    get_user_by_number,
    create_user,
    create_session,
    update_session,
    get_user_session,
    create_turn,
    create_message,
    get_plugin_reference,
)
from ...utils import extract_reference_id

logger = logging.getLogger("jb-manager-api")


async def handle_webhook(webhook_data: str) -> AsyncGenerator[FlowInput, None]:
    plugin_uuid = extract_reference_id(webhook_data)
    if not plugin_uuid:
        raise ValueError("Plugin UUID not found in webhook data")
    logger.info("Plugin UUID: %s", plugin_uuid)
    plugin_reference = await get_plugin_reference(plugin_uuid)
    logger.info("Webhook Data: %s", webhook_data)
    flow_input = FlowInput(
        source="api",
        session_id=plugin_reference.session_id,
        turn_id=plugin_reference.turn_id,
        plugin_input=json.loads(webhook_data),
    )
    yield flow_input


async def handle_callback(callback_data: Dict) -> AsyncGenerator[ChannelInput, None]:
    bot_number = WhatsappHelper.extract_whatsapp_business_number(callback_data)
    channel = await get_active_channel_by_identifier(bot_number, "whatsapp")
    if channel is None:
        logger.error("Active channel not found for number %s", bot_number)
        raise ValueError("Active channel not found")

    channel_id: str = channel.id
    for message in WhatsappHelper.process_messsage(callback_data):
        contact_number = message["from"]
        user = await get_user_by_number(contact_number, channel_id)
        turn_id = str(uuid.uuid4())

        if user is None:
            # register user
            logger.info("Registering user")
            contact_name = message["name"]
            user = await create_user(
                channel_id, contact_number, contact_name, contact_name
            )
        user_id: str = user.id

        create_new_session = False
        message_type = message["type"]
        if message_type == "text":
            message_text = message[message_type]["body"]
            if message_text.lower() == "hi":
                create_new_session = True

        if create_new_session:
            # create session
            logger.info("Creating session")
            session = await create_session(user_id, channel_id)
        else:
            session = await get_user_session(channel_id, user_id, 24 * 60 * 60 * 1000)
            if session is None:
                # create session
                logger.info("Creating session")
                session = await create_session(user_id, channel_id)
            else:
                await update_session(session.id)
        session_id: str = session.id

        message_type = message["type"]
        if message_type == "interactive":
            message_type = (
                "form" if message[message_type]["type"] == "nfm_reply" else message_type
            )
            message["type"] = message_type
            message[message_type] = message.pop("interactive")

        turn_id = await create_turn(
            session_id=session_id,
            channel_id=channel_id,
            turn_type=message_type,
            channel="WA",
        )
        msg_id = await create_message(
            turn_id=turn_id,
            message_type=message_type,
            channel="WA",
            channel_id=message["id"],
            is_user_sent=True,
        )

        # remove mobile number
        message.pop("from")

        channel_input = ChannelInput(
            source="api",
            session_id=session_id,
            message_id=msg_id,
            turn_id=turn_id,
            intent=ChannelIntent.BOT_IN,
            channel_data=ChannelData(**message),
            data=BotInput(
                message_type=MessageType.TEXT,
                message_data=MessageData(message_text="dummy"),
            ),
        )

        # write to channel
        yield channel_input
