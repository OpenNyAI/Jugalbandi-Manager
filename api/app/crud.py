from typing import Sequence
import logging
import uuid
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from lib.db_session_handler import DBSessionHandler
from lib.models import (
    JBWebhookReference,
    JBSession,
    JBTurn,
    JBUser,
    JBBot,
    JBChannel,
    JBApiLogger,
)

logger = logging.getLogger("jb-manager-api")


async def create_user(channel_id: str, phone_number: str, first_name: str, last_name: str) -> JBUser:
    """Create a new user and return the user object."""
    user = JBUser(
        id=str(uuid.uuid4()),
        channel_id=channel_id,
        first_name=first_name,
        last_name=last_name,
        identifier=phone_number,
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(user)
            await session.commit()
            logger.info(f"Created user: {user.id}")
            return user


async def get_user_by_number(number: str, channel_id: str) -> JBUser:
    """Fetch a user by phone number and channel ID."""
    query = select(JBUser).where(
        JBUser.identifier == number, JBUser.channel_id == channel_id
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            user = result.scalars().first()
            logger.debug(f"Fetched user for number {number}: {user.id if user else 'None'}")
            return user


async def create_turn(bot_id: str, channel_id: str, user_id: str) -> str:
    """Create a new conversation turn and return the turn ID."""
    turn_id = str(uuid.uuid4())
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(JBTurn(id=turn_id, bot_id=bot_id, channel_id=channel_id, user_id=user_id))
            await session.commit()
            logger.info(f"Created turn: {turn_id} for bot: {bot_id}, user: {user_id}")
            return turn_id


async def get_bot_by_id(bot_id: str) -> JBBot:
    """Retrieve bot details including its channels."""
    query = select(JBBot).options(joinedload(JBBot.channels)).where(JBBot.id == bot_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            bot = result.scalars().unique().first()
            return bot


async def get_chat_history(bot_id: str, skip=0, limit=1000):
    """Get chat history of a bot with optional pagination."""
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(JBSession, JBUser)
                .join(JBUser, JBSession.user_id == JBUser.id)
                .join(JBChannel, JBSession.channel_id == JBChannel.id)
                .where(JBChannel.bot_id == bot_id)
                .offset(skip)
                .limit(limit)
            )
            history = [list(row) for row in result]
            logger.debug(f"Fetched {len(history)} chat history records for bot: {bot_id}")
            return history


async def get_plugin_reference(plugin_uuid: str) -> JBWebhookReference:
    """Fetch plugin reference by UUID."""
    query = select(JBWebhookReference).where(JBWebhookReference.id == plugin_uuid)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().first()


async def get_bot_list():
    """Return a list of all active bots."""
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            query = select(JBBot).options(joinedload(JBBot.channels)).where(JBBot.status != "deleted")
            result = await session.execute(query)
            return result.scalars().unique().all()


async def get_bot_chat_sessions(bot_id: str, session_id: str):
    """Retrieve chat sessions of a bot for a given session ID."""
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(JBSession)
                .join(JBTurn, JBTurn.bot_id == bot_id)
                .join(JBChannel, JBSession.channel_id == JBChannel.id)
                .where(JBChannel.bot_id == bot_id, JBSession.id == session_id)
                .options(joinedload(JBSession.turns).joinedload(JBTurn.messages))
            )
            return result.unique().scalars().all()


async def update_bot(bot_id: str, data):
    """Update bot fields and return bot ID."""
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            stmt = update(JBBot).where(JBBot.id == bot_id).values(**data)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Updated bot: {bot_id} with data: {data}")
            return bot_id


async def create_bot(data):
    """Create a new bot instance and return the bot object."""
    bot_id = str(uuid.uuid4())
    bot = JBBot(id=bot_id, **{key: data.get(key) for key in ["name", "dsl", "code", "requirements", "index_urls", "required_credentials", "version"]})
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(bot)
            await session.commit()
            logger.info(f"Created bot: {bot_id}")
            return bot


async def create_channel(bot_id, data):
    """Create a new channel for a bot."""
    channel_id = str(uuid.uuid4())
    channel = JBChannel(
        id=channel_id,
        bot_id=bot_id,
        name=data.get("name"),
        type=data.get("type"),
        key=data.get("key"),
        app_id=data.get("app_id"),
        url=data.get("url"),
        status=data.get("status", "inactive"),
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(channel)
            await session.commit()
            logger.info(f"Created channel: {channel_id} for bot: {bot_id}")
            return channel


async def get_channels_by_identifier(identifier: str, channel_type: str) -> Sequence[JBChannel] | None:
    """Fetch channels by identifier and type excluding deleted ones."""
    query = select(JBChannel).options(joinedload(JBChannel.bot)).where(
        JBChannel.app_id == identifier,
        JBChannel.type == channel_type,
        JBChannel.status != "deleted",
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().unique().all()


async def get_active_channel_by_identifier(identifier: str, channel_type: str) -> JBChannel | None:
    """Return the active channel based on identifier and type."""
    query = select(JBChannel).options(joinedload(JBChannel.bot)).where(
        JBChannel.app_id == identifier,
        JBChannel.type == channel_type,
        JBChannel.status == "active",
    )
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().unique().first()


async def get_channel_by_id(channel_id: str) -> JBChannel | None:
    """Fetch channel by its ID."""
    query = select(JBChannel).where(JBChannel.id == channel_id)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            return result.scalars().first()


async def update_channel(channel_id: str, data):
    """Update channel fields and return channel ID."""
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            stmt = update(JBChannel).where(JBChannel.id == channel_id).values(**data)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Updated channel: {channel_id} with data: {data}")
            return channel_id


async def update_channel_by_bot_id(bot_id: str, data):
    """Update channel based on bot ID and return bot ID."""
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            stmt = update(JBChannel).where(JBChannel.bot_id == bot_id).values(**data)
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Updated channels for bot: {bot_id} with data: {data}")
            return bot_id