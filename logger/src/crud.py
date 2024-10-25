from lib.db_session_handler import DBSessionHandler
from lib.models import (
    JBApiLogger,
    JBChannelLogger,
)

async def create_api_logger(
    msg_id: str, user_id: str, turn_id: str, session_id: str, status: str, 
) -> JBApiLogger:
    api_logger_data = JBApiLogger(
        msg_id = msg_id,
        user_id = user_id,
        turn_id = turn_id,
        session_id = session_id, 
        status = status,
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(api_logger_data)
            await session.commit()
            return api_logger_data
    return None

async def create_channel_logger(
        id: str, 
        turn_id: str, 
        channel_id: str, 
        channel_name: str, 
        msg_intent: str, 
        msg_type: str, 
        sent_to_service: str, 
        status: str) -> JBChannelLogger:
    channel_logger_data = JBChannelLogger(
                    id = id,
                    turn_id = turn_id,
                    channel_id = channel_id,
                    channel_name = channel_name,
                    msg_intent = msg_intent,
                    msg_type = msg_type,
                    sent_to_service = sent_to_service,
                    status = status
                    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(channel_logger_data)
            await session.commit()
            return channel_logger_data
    return None
    