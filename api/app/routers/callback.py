import uuid
from fastapi import Request, APIRouter
from lib.whatsapp import WhatsappHelper
from lib.data_models import ChannelData, ChannelInput, ChannelIntent, BotInput, MessageData, MessageType
from lib.jb_logging import Logger
from ..crud import get_bot_by_phone_number, get_user_by_number, create_user, create_session, create_message, create_turn, update_session, get_user_session
from ..extensions import produce_message, channel_topic

logger = Logger("jb-manager-api")
router = APIRouter(
    prefix="",
)

@router.post("/callback")
async def callback(request: Request):
    # if whatsapp parse with whatsapp library
    # if telegram parse with telegram library:
    data = await request.json()

    # TODO - write code to differentiate channel and identify helper to use

    bot_number = WhatsappHelper.extract_whatsapp_business_number(data)
    bot = await get_bot_by_phone_number(bot_number)
    bot_id = bot.id
    if bot_id is None:
        logger.error(f"Bot not found for number {bot_number}")
        return 404

    for message in WhatsappHelper.process_messsage(data):
        contact_number = message["from"]
        contact_name = message["name"]  # Set to Dummy at the moment
        user = await get_user_by_number(contact_number, bot_id)
        turn_id = str(uuid.uuid4())

        if user is None:
            # register user
            logger.info("Registering user")
            user = await create_user(bot_id, contact_number, contact_name, contact_name)

        create_new_session = False
        message_type = message["type"]
        if message_type == "text":
            message_text = message[message_type]["body"]
            if message_text.lower() == "hi":
                create_new_session = True

        if create_new_session:
            # create session
            logger.info("Creating session")
            session = await create_session(user.id, bot_id)
        else:
            session = await get_user_session(bot_id, user.id, 24 * 60 * 60 * 1000)
            if session is None:
                # create session
                logger.info("Creating session")
                session = await create_session(user.id, bot_id)
            else:
                await update_session(session.id)

        message_type = message["type"]
        if message_type == "interactive":
            message_type = (
                "form" if message[message_type]["type"] == "nfm_reply" else message_type
            )
            message["type"] = message_type
            message[message_type] = message.pop("interactive")

        turn_id = await create_turn(
            session_id=session.id,
            bot_id=bot_id,
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
            session_id=session.id,
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
        produce_message(channel_input.model_dump_json(), topic=channel_topic)

    return 200
