import asyncio
import json
import logging
import os
import sys
import traceback

from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from openai import OpenAI

from lib.data_models import Flow,FlowIntent, Callback, CallbackType, RAG, RAGResponse
from lib.kafka_utils import KafkaConsumer, KafkaProducer

load_dotenv()

print("Inside Retriever", file=sys.stderr)

kafka_broker = os.getenv("KAFKA_BROKER")
retriever_topic = os.getenv("KAFKA_RETRIEVER_TOPIC")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")

print("Connecting", file=sys.stderr)

client = OpenAI()
db_name = os.getenv("POSTGRES_DATABASE_NAME")
db_user = os.getenv("POSTGRES_DATABASE_USERNAME")
db_password = os.getenv("POSTGRES_DATABASE_PASSWORD")
db_host = os.getenv("POSTGRES_DATABASE_HOST")
db_port = os.getenv("POSTGRES_DATABASE_PORT")
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
producer = KafkaProducer.from_env_vars()

print("Connections done", file=sys.stderr)

logger = logging.getLogger("retriever")


def send_message(data):
    # logger.info(f"Sending message to {flow_topic}, msg_id:", data['msg_id'])
    producer.send_message(flow_topic, data)


async def querying_with_langchain(
    source: str,
    turn_id: str,
    collection_name: str,
    query: str,
    top_chunk_k_value: int = 5,
    metadata: dict = None,
    callback: callable = None,
):
    print(query, collection_name, top_chunk_k_value)
    if os.environ["OPENAI_API_TYPE"] == "azure":
        embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-ada-002",
            azure_deployment=os.environ["AZURE_DEPLOYMENT_NAME"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            openai_api_type=os.environ["OPENAI_API_TYPE"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
        )
    else:
        embeddings = OpenAIEmbeddings(client="")

    search_index = PGVector(
        collection_name=collection_name,
        connection=db_url,
        embeddings=embeddings,
    )
    # TODO: Check metadata is not None and add it to the search_index filter
    if metadata:
        documents = search_index.similarity_search(
            query=query, k=top_chunk_k_value, filter=metadata
        )
    else:
        documents = search_index.similarity_search(query=query, k=top_chunk_k_value)
    data = []
    for document in documents:
        data.append({"chunk": document.page_content, "metadata": document.metadata})
    flow_input = Flow(source="retriever", intent=FlowIntent.CALLBACK,callback=Callback(turn_id=turn_id,callback_type=CallbackType.RAG,rag_response=data))
    # logging.info("flow Input %s", flow_input)

    if callback:
        callback(flow_input.model_dump_json())


while True:
    try:
        # will keep trying until non-null message is received
        message = consumer.receive_message(retriever_topic, timeout=1.0)
        data = json.loads(message)
        data = RAG(**data)
        retriver_input = data.model_dump(
            include={
                "source",
                "turn_id",
                "collection_name",
                "query",
                "top_chunk_k_value",
            }
        )
        # Doubt: What is metadata in querying_with_langchain?
        asyncio.run(querying_with_langchain(**retriver_input, callback=send_message))
    except Exception as e:
        logger.error("Exception %s :: %s", e, traceback.format_exc())
