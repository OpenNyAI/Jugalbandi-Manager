from fastapi import APIRouter
from .bot import router as bot_router
from .channel import router as channel_router

router = APIRouter(
    prefix="/v2",
)
router.include_router(bot_router)
router.include_router(channel_router)
