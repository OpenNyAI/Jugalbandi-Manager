from sqlalchemy import select

from lib.db_session_handler import DBSessionHandler
from lib.models import JBMessage, JBTurn, JBUser, JBSession


async def get_user_preferred_language(session_id: str):
    query = select(JBSession.pid).where(JBSession.id == session_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            pid = result.scalars().first()
            preferred_language = await get_user_preferred_language_by_pid(pid)
            return preferred_language


async def get_user_preferred_language_by_pid(pid: str):
    query = select(JBUser.language_preference).where(JBUser.id == pid)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            preferred_language = result.scalars().first()
            return preferred_language


async def get_message_media_information(msg_id: str):
    query = select(JBMessage).where(JBMessage.id == msg_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            message = result.scalars().first()
            return message


async def get_turn_information(turn_id: str):
    query = select(JBTurn).where(JBTurn.id == turn_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            turn = result.scalars().first()
            return turn
