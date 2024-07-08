import uuid
from typing import Tuple
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from lib.db_session_handler import DBSessionHandler

from lib.models import JBSession, JBUser, JBMessage, JBChannel


async def get_user_by_session_id(session_id: str) -> JBUser | None:
    query = (
        select(JBSession)
        .options(joinedload(JBSession.user))
        .where(JBSession.id == session_id)
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            if s is not None:
                user = s.user
                return user
    return None


async def get_channel_by_session_id(session_id: str) -> Tuple[str, str] | None:
    query = (
        select(JBSession)
        .options(joinedload(JBSession.channel))
        .where(JBSession.id == session_id)
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            if s is not None:
                channel: JBChannel = s.channel
                return channel.app_id, channel.key


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
