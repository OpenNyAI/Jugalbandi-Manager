from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chats_router, bots_router, webhook_router, callback_router

app = FastAPI()
app.include_router(bots_router)
app.include_router(chats_router)
app.include_router(callback_router)
app.include_router(webhook_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)