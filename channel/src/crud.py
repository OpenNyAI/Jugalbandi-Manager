import uuid
from sqlalchemy import select, update

from lib.db_session_handler import DBSessionHandler

from lib.models import JBSession, JBUser, JBMessage, JBBot


async def get_user_by_session_id(session_id: str):
    # TODO: have to make it as single query
    query = select(JBSession).where(JBSession.id == session_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            if s is not None:
                query = select(JBUser).where(JBUser.id == s.pid)
                result = await session.execute(query)
                user = result.scalars().first()
                return user
    return None


async def get_bot_by_session_id(session_id: str):
    # TODO: have to make it as single query
    query = select(JBSession).where(JBSession.id == session_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            if s is not None:
                query = select(JBBot).where(JBBot.id == s.bot_id)
                result = await session.execute(query)
                bot = result.scalars().first()
                return bot.phone_number, bot.channels
    return None


async def set_user_language(session_id: str, language: str):
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            query = select(JBSession).where(JBSession.id == session_id)
            result = await session.execute(query)
            s = result.scalars().first()
            if s is not None:
                query = (
                    update(JBUser)
                    .where(JBUser.id == s.pid)
                    .values(language_preference=language)
                )
                await session.execute(query)
                await session.commit()
                return True
    return None


async def update_message(msg_id: str, **kwargs):
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            query = update(JBMessage).where(JBMessage.id == msg_id).values(**kwargs)
            await session.execute(query)
            await session.commit()
            return True
    return None


async def create_message(
    turn_id: str,
    message_type: str,
    channel: str,
    channel_id: str,
    is_user_sent: bool = False,
    message_text: str = None,
    media_url: str = None,
):
    message_id = str(uuid.uuid4())
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(
                JBMessage(
                    id=message_id,
                    turn_id=turn_id,
                    message_type=message_type,
                    channel=channel,
                    channel_id=channel_id,
                    is_user_sent=is_user_sent,
                    message_text=message_text,
                    media_url=media_url,
                )
            )
            await session.commit()
            return message_id
    return None
