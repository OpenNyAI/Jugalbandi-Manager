import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .handlers import handle_callback, handle_webhook
from .extensions import flow_topic, produce_message
from .routers import v1_router

load_dotenv()
logger = logging.getLogger("jb-manager-api")

app = FastAPI()
app.include_router(v1_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/callback")
async def callback(request: Request):
    data = await request.json()

    async for channel_input in handle_callback(data):
        produce_message(channel_input.model_dump_json())

    return 200


@app.post("/webhook")
async def plugin_webhook(request: Request):
    webhook_data = await request.body()
    webhook_data = webhook_data.decode("utf-8")
    try:
        async for flow_input in handle_webhook(webhook_data):
            produce_message(flow_input.model_dump_json(), topic=flow_topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return 200
