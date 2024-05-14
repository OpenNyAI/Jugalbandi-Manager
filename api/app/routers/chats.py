from fastapi import APIRouter
from ..crud import get_chat_history, get_bot_chat_sessions

router = APIRouter(
    prefix="",
)

# get all messages related to a session
@router.get("/chats/{bot_id}/sessions/{session_id}")
async def get_session(bot_id: str, session_id: str):
    sessions = await get_bot_chat_sessions(bot_id, session_id)
    return sessions


# get all chats related to a bot
@router.get("/chats/{bot_id}")
async def get_chats(bot_id: str, skip: int = 0, limit: int = 100):
    chats = await get_chat_history(bot_id, skip, limit)
    return chats


@router.get("/chats")
async def get_chats(bot_id: str) -> list:
    chats = await get_chat_history(bot_id)
    return chats