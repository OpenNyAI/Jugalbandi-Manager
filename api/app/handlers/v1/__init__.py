import logging
import uuid
from typing import Dict, AsyncGenerator
from lib.whatsapp import WhatsappHelper
from lib.data_models import (
    Channel,
    ChannelIntent,
    RestBotInput,
    Flow,
    FlowIntent,
    Callback,
    CallbackType,
)
from ...crud import (
    get_active_channel_by_identifier,
    get_user_by_number,
    create_user,
    create_turn,
    get_plugin_reference,
)
from ...utils import extract_reference_id

logger = logging.getLogger("jb-manager-api")


async def handle_webhook(webhook_data: str) -> AsyncGenerator[Flow, None]:
    plugin_uuid = extract_reference_id(webhook_data)
    if not plugin_uuid:
        raise ValueError("Plugin UUID not found in webhook data")
    logger.info("Plugin UUID: %s", plugin_uuid)
    plugin_reference = await get_plugin_reference(plugin_uuid)
    turn_id: str = plugin_reference.turn_id
    logger.info("Webhook Data: %s", webhook_data)
    flow_input = Flow(
        source="api",
        intent=FlowIntent.CALLBACK,
        callback=Callback(
            turn_id=turn_id,
            callback_type=CallbackType.EXTERNAL,
            external=webhook_data,
        ),
    )
    yield flow_input


async def handle_callback(
    callback_data: Dict, headers: Dict, query_params: Dict
) -> AsyncGenerator[Channel, None]:
    bot_number = WhatsappHelper.extract_whatsapp_business_number(callback_data)
    jb_channel = await get_active_channel_by_identifier(bot_number, "whatsapp")
    if jb_channel is None:
        logger.error("Active channel not found for number %s", bot_number)
        raise ValueError("Active channel not found")

    channel_id: str = jb_channel.id
    for message in WhatsappHelper.process_messsage(callback_data):
        contact_number = message["from"]
        jb_user = await get_user_by_number(contact_number, channel_id)
        turn_id = str(uuid.uuid4())

        if jb_user is None:
            # register user
            logger.info("Registering user")
            contact_name = message["name"]
            jb_user = await create_user(
                channel_id, contact_number, contact_name, contact_name
            )
        user_id: str = jb_user.id

        turn_id = await create_turn(
            bot_id=jb_channel.bot.id, channel_id=channel_id, user_id=user_id
        )
        msg_type = message["type"]
        message = {
            k: v for k, v in message.items() if k in ["type", "timestamp", msg_type]
        }
        channel_input = Channel(
            source="api",
            turn_id=turn_id,
            intent=ChannelIntent.CHANNEL_IN,
            bot_input=RestBotInput(
                channel_name="whatsapp",
                headers=headers,
                data=message,
                query_params=query_params,
            ),
        )

        # write to channel
        yield channel_input
