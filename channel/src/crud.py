import uuid
from typing import Dict
from sqlalchemy import select
from lib.db_session_handler import DBSessionHandler
from lib.models import JBUser, JBMessage, JBChannel, JBForm, JBTurn

async def get_channel_by_turn_id(turn_id: str) -> JBChannel | None:
    query = (
        select(JBChannel)
        .join(JBTurn, JBChannel.id == JBTurn.channel_id)
        .where(JBTurn.id == turn_id)
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            return s


async def create_message(
    turn_id: str,
    message_type: str,
    message: Dict,
    is_user_sent: bool = False,
):
    message_id = str(uuid.uuid4())
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(
                JBMessage(
                    id=message_id,
                    turn_id=turn_id,
                    message_type=message_type,
                    is_user_sent=is_user_sent,
                    message=message,
                )
            )
            await session.commit()
            return message_id
    return None


async def get_form_parameters(channel_id, form_id):
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(JBForm)
                .where(JBForm.channel_id == channel_id)
                .where(JBForm.form_uid == form_id)
            )
            s = result.scalars().first()
            return s.parameters


async def get_user_by_turn_id(turn_id: str) -> JBUser | None:
    query = (
        select(JBUser)
        .join(JBTurn, JBUser.id == JBTurn.user_id)
        .where(JBTurn.id == turn_id)
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            return s
