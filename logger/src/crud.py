from lib.db_session_handler import DBSessionHandler
from lib.models import (
    JBApiLogger,
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
