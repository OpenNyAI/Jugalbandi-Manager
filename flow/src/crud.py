import uuid
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from lib.db_session_handler import DBSessionHandler
from lib.models import JBFSMState, JBSession, JBPluginUUID, JBBot


async def get_state_by_pid(pid: str) -> JBFSMState:
    query = select(JBFSMState).where(JBFSMState.pid == pid)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            state = result.scalars().first()
            return state
    return None


async def insert_state(pid: str, state: str, variables: dict = dict()) -> JBFSMState:
    state_id = str(uuid.uuid4())
    state = JBFSMState(id=state_id, pid=pid, state=state, variables=variables)
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            session.add(state)
            await session.commit()
            return state
    return None


async def update_state_and_variables(
    pid: str, state: str, variables: dict
) -> JBFSMState:
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            # await session.query(JBFSMState).filter(JBFSMState.pid == pid).update({"state": state, "variables": variables})
            stmt = (
                update(JBFSMState)
                .where(JBFSMState.pid == pid)
                .values(state=state, variables=variables)
            )
            await session.execute(stmt)
            await session.commit()
            return state
    return None


async def get_session_with_bot(session_id: str):
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(JBSession)
                .options(joinedload(JBSession.bot))
                .join(JBBot, JBSession.bot_id == JBBot.id)
                .where(JBSession.id == session_id)
            )
            s = result.scalars().first()
            return s


async def get_bot_by_id(bot_id: str) -> JBBot | None:
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(select(JBBot).where(JBBot.id == bot_id))
            s = result.scalars().first()
            return s


async def get_all_bots():
    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(JBBot).where(JBBot.status != "deleted")
            )
            s = result.scalars().all()
            return s


async def get_pid_by_session_id(session_id: str):
    # Create a query to select JBSession based on the provided session_id
    query = select(JBSession.pid).where(JBSession.id == session_id)

    async with DBSessionHandler.get_async_session() as session:
        async with session.begin():
            result = await session.execute(query)
            s = result.scalars().first()
            return s


def insert_jb_plugin_uuid(session_id: str, turn_id: str):
    # Create a query to insert a new row into JBPluginMapping
    JB_IDENTIFIER = "jbkey"
    reference_id = f"{JB_IDENTIFIER}{str(uuid.uuid4())[:25]}{JB_IDENTIFIER}"
    plugin_uid = JBPluginUUID(id=reference_id, session_id=session_id, turn_id=turn_id)

    with DBSessionHandler.get_sync_session() as session:
        with session.begin():
            session.add(plugin_uid)
            session.commit()
            return reference_id
    return False
