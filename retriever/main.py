import asyncio
import json
import logging
import os
import sys
import traceback

from dotenv import load_dotenv
from langchain_community.vectorstores import PGVector
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from lib.data_models import FlowInput, RAGInput
from lib.kafka_utils import KafkaConsumer, KafkaProducer
from openai import OpenAI
from r2r import R2R, EmbeddingConfig, R2RBuilder, VectorSearchSettings
from r2r.providers.embeddings import AzureOpenAIEmbeddingProvider

load_dotenv()

print("Inside Retriever", file=sys.stderr)

kafka_broker = os.getenv("KAFKA_BROKER")
retriever_topic = os.getenv("KAFKA_RETRIEVER_TOPIC")
flow_topic = os.getenv("KAFKA_FLOW_TOPIC")

print("Connecting", file=sys.stderr)

consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
producer = KafkaProducer.from_env_vars()

print("Connections done", file=sys.stderr)

logger = logging.getLogger("retriever")

client = OpenAI()
db_name = os.getenv("POSTGRES_DATABASE_NAME")
db_user = os.getenv("POSTGRES_DATABASE_USERNAME")
db_password = os.getenv("POSTGRES_DATABASE_PASSWORD")
db_host = os.getenv("POSTGRES_DATABASE_HOST")
db_port = os.getenv("POSTGRES_DATABASE_PORT")
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_r2r():
    if os.getenv("OPENAI_API_TYPE") == "azure":
        embedding_provider = AzureOpenAIEmbeddingProvider(
            EmbeddingConfig(
                provider="azure-openai",
                base_model="text-embedding-3-large",
                base_dimension=512,
            )
        )
        return R2RBuilder().with_embedding_provider(provider=embedding_provider).build()
    return R2R()


def get_embeddings():
    if os.getenv("OPENAI_API_TYPE") == "azure":
        return AzureOpenAIEmbeddings(
            model="text-embedding-ada-002",
            azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            openai_api_type=os.getenv("OPENAI_API_TYPE"),
            openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
    return OpenAIEmbeddings(client="")


def send_message(data):
    producer.send_message(flow_topic, data)


async def querying(
    session_id: str,
    turn_id: str,
    collection_name: str,
    query: str,
    top_chunk_k_value: int = 5,
    metadata: dict = None,
    callback: callable = None,
):
    if os.getenv("RETRIEVER_TYPE") == "r2r":
        r2r_app = get_r2r()
        vector_search_settings = (
            VectorSearchSettings(
                search_filters=metadata, search_limit=top_chunk_k_value
            )
            if metadata
            else VectorSearchSettings()
        )
        search_results = await r2r_app.engine.asearch(
            query=query,
            vector_search_settings=vector_search_settings,
        )
        data = []
        for chunk in search_results["vector_search_results"][:5]:
            chunk_text = chunk["metadata"].pop("text", None)
            data.append({"chunk": chunk_text, "metadata": chunk["metadata"]})
    else:
        embeddings = get_embeddings()
        search_index = PGVector(
            collection_name=collection_name,
            connection_string=db_url,
            embedding_function=embeddings,
        )
        documents = (
            search_index.similarity_search(
                query=query, k=top_chunk_k_value, filter=metadata
            )
            if metadata
            else search_index.similarity_search(query=query, k=top_chunk_k_value)
        )
        data = [
            {"chunk": document.page_content, "metadata": document.metadata}
            for document in documents
        ]
    flow_input = {
        "source": "retriever",
        "session_id": session_id,
        "turn_id": turn_id,
        "rag_response": data,
    }
    flow_input = FlowInput(**flow_input)

    if callback:
        callback(flow_input.model_dump_json())


while True:
    try:
        # will keep trying until non-null message is received
        message = consumer.receive_message(retriever_topic, timeout=1.0)
        data = json.loads(message)
        data = RAGInput(**data)
        retriever_input = data.model_dump(
            include={
                "session_id",
                "turn_id",
                "collection_name",
                "query",
                "top_chunk_k_value",
            }
        )
        asyncio.run(querying(**retriever_input, callback=send_message))
    except Exception as e:
        logger.error("Exception %s :: %s", e, traceback.format_exc())
