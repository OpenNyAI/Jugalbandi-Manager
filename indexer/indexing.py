import asyncio
import io
import json
import logging
import os

import asyncpg
import docx2txt
import fitz
import pandas as pd
from dotenv import load_dotenv
from fastapi.datastructures import UploadFile
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from lib.data_models import Indexer
from lib.file_storage import StorageHandler
from lib.kafka_utils import KafkaConsumer
from model import InternalServerException
from r2r import R2R, EmbeddingConfig, R2RBuilder
from r2r.providers.embeddings import AzureOpenAIEmbeddingProvider

load_dotenv()

kafka_bootstrap_servers = os.getenv("KAFKA_BROKER")
kafka_topic = os.getenv("KAFKA_CONSUMER_TOPIC")
print("kafka_bootstrap_servers", kafka_bootstrap_servers)
print("kafka", kafka_topic)
consumer = KafkaConsumer.from_env_vars(
    group_id="cooler_group_id", auto_offset_reset="latest"
)
logging.basicConfig()
logger = logging.getLogger("indexer")
logger.setLevel(logging.INFO)
storage = StorageHandler.get_async_instance()


def parse_file(file_path: str) -> str:
    parsers = {
        ".pdf": pdf_parser,
        ".docx": docx_parser,
        ".xlsx": xlsx_parser,
        ".json": json_parser,
    }
    _, ext = os.path.splitext(file_path)
    parser = parsers.get(ext, default_parser)
    return parser(file_path)


def docx_parser(docx_file_path: str):
    return docx2txt.process(docx_file_path)


def pdf_parser(pdf_file_path: str):
    doc = fitz.open(pdf_file_path)
    return "\n".join(page.get_text("text") for page in doc)


def xlsx_parser(excel_file_path: str):
    df = pd.read_excel(excel_file_path)
    return df.to_string(index=False)


def json_parser(json_file_path: str):
    with open(json_file_path, "r") as file:
        data = json.load(file)
    return json.dumps(data, indent=4)


def default_parser(file_path: str):
    with open(file_path, "r") as file:
        return file.read()


class TextConverter:
    async def textify(self, filepath: str) -> str:
        return parse_file(filepath)


class DataIndexer:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=4 * 1024,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        self.db_name = os.getenv("POSTGRES_DATABASE_NAME")
        self.db_user = os.getenv("POSTGRES_DATABASE_USERNAME")
        self.db_password = os.getenv("POSTGRES_DATABASE_PASSWORD")
        self.db_host = os.getenv("POSTGRES_DATABASE_HOST")
        self.db_port = os.getenv("POSTGRES_DATABASE_PORT")
        self.db_url = f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        os.environ["POSTGRES_DBNAME"] = self.db_name
        os.environ["POSTGRES_USER"] = self.db_user
        os.environ["POSTGRES_PASSWORD"] = self.db_password
        os.environ["POSTGRES_HOST"] = self.db_host
        os.environ["POSTGRES_PORT"] = self.db_port
        self.text_converter = TextConverter()

    async def create_pg_vector_index_if_not_exists(self):
        connection = await asyncpg.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            port=self.db_port,
        )
        try:
            async with connection.transaction():
                await connection.execute(
                    "ALTER TABLE langchain_pg_embedding ALTER COLUMN embedding TYPE vector(1536)"
                )
                await connection.execute(
                    "CREATE INDEX IF NOT EXISTS langchain_embeddings_hnsw ON langchain_pg_embedding USING hnsw (embedding vector_cosine_ops)"
                )
        finally:
            await connection.close()

    async def index(self, indexer_input: Indexer):
        source_files = []
        source_chunks = []
        counter = 0
        for file_path in indexer_input.files:
            async with storage.read_file(file_path=file_path, mode="rb") as file:
                file_content = await file.read()
                file_path = file.name
                if indexer_input.type == "r2r":
                    source_files.append(
                        UploadFile(
                            file=io.BytesIO(file_content),
                            size=len(file_content),
                            filename=os.path.basename(file_path),
                        )
                    )
                else:
                    content = await self.text_converter.textify(file_path)
                    for chunk in self.splitter.split_text(content):
                        new_metadata = {
                            "chunk-id": str(counter),
                            "document_name": os.path.basename(file_path),
                        }
                        source_chunks.append(
                            Document(page_content=chunk, metadata=new_metadata)
                        )
                        counter += 1
        try:
            if indexer_input.type == "r2r":
                os.environ["POSTGRES_VECS_COLLECTION"] = indexer_input.collection_name
                r2r_app = await self.get_r2r()
                await r2r_app.engine.aingest_files(files=source_files)
            else:
                embeddings = await self.get_embeddings()
                vector_db = PGVector.from_documents(
                    embedding=embeddings,
                    documents=source_chunks,
                    collection_name=indexer_input.collection_name,
                    connection_string=self.db_url,
                    pre_delete_collection=True,
                )
                await self.create_pg_vector_index_if_not_exists()
            print(
                f"Embeddings have been created for the collection: {indexer_input.collection_name}"
            )
        except Exception as e:
            raise InternalServerException(e.__str__())

    async def get_r2r(self):
        if os.getenv("OPENAI_API_TYPE") == "azure":
            embedding_provider = AzureOpenAIEmbeddingProvider(
                EmbeddingConfig(
                    provider="azure-openai",  # provider name for azure
                    base_model=os.getenv("AZURE_EMBEDDING_MODEL_NAME"),
                    base_dimension=512,  # default parameter
                )
            )
            return (
                R2RBuilder()
                .with_embedding_provider(provider=embedding_provider)
                .build()
            )
        return R2R()

    async def get_embeddings(self):
        if os.getenv("OPENAI_API_TYPE") == "azure":
            return AzureOpenAIEmbeddings(
                model=os.getenv("AZURE_EMBEDDING_MODEL_NAME"),
                azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                openai_api_type=os.getenv("OPENAI_API_TYPE"),
                openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            )
        return OpenAIEmbeddings(client="")


async def start_indexer():
    """Starts the indexer server"""
    indexer = DataIndexer()
    logger.info("Starting Listening")
    while True:
        message = consumer.receive_message(kafka_topic)
        print("Indexer Message:", message)
        data = json.loads(message)
        indexer_input = Indexer(**data)

        asyncio.run(indexer.index(indexer_input))


if __name__ == "__main__":
    asyncio.run(start_indexer())
