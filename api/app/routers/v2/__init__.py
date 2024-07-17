from fastapi import APIRouter
from .bot import router as bot_router
from .channel import router as channel_router
from .callback import router as callback_router

router = APIRouter(
    prefix="/v2",
    tags=["v2"],
)
router.include_router(bot_router)
router.include_router(channel_router)
router.include_router(callback_router)
