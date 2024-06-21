import asyncio
import json
import os

import asyncpg
import docx2txt
import fitz
import pandas as pd
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from model import InternalServerException

from lib.data_models import IndexerInput
from lib.kafka_utils import KafkaConsumer

load_dotenv()

kafka_bootstrap_servers = os.getenv("KAFKA_BROKER")
kafka_topic = os.getenv("KAFKA_CONSUMER_TOPIC")
print("kafka_bootstrap_servers", kafka_bootstrap_servers)
print("kafka", kafka_topic)
consumer = KafkaConsumer.from_env_vars(
    group_id="test_grp_id", auto_offset_reset="latest"
)


def docx_parser(docx_file_path):
    text = docx2txt.process(docx_file_path)
    return text


def pdf_parser(pdf_file_path):
    doc = fitz.open(pdf_file_path)
    content = "\n"
    for page in doc:
        text = page.get_text("text", textpage=None, sort=False)
        content += text
    return content


def xlsx_parser(excel_file_path):
    df = pd.read_excel(excel_file_path)
    text = df.to_string(index=False)
    return text


def json_parser(json_file_path):
    file = open(json_file_path, "r")
    data = json.load(file)
    text = json.dumps(data, indent=4)
    return text


class TextConverter:
    async def textify(self, filepath: str) -> str:
        if filepath.endswith(".pdf"):
            content = pdf_parser(filepath)
        elif filepath.endswith(".docx"):
            content = docx_parser(filepath)
        elif filepath.endswith(".xlsx"):
            content = xlsx_parser(filepath)
        elif filepath.endswith(".json"):
            content = json_parser(filepath)
        else:
            with open(filepath, "r") as f:
                content = f.read()
        return content


class LangchainIndexer:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=4 * 1024, chunk_overlap=0, separators=["\n\n", "\n", ".", ""]
        )
        self.db_name = os.getenv("POSTGRES_DATABASE_NAME")
        self.db_user = os.getenv("POSTGRES_DATABASE_USERNAME")
        self.db_password = os.getenv("POSTGRES_DATABASE_PASSWORD")
        self.db_host = os.getenv("POSTGRES_DATABASE_HOST")
        self.db_port = os.getenv("POSTGRES_DATABASE_PORT")
        self.db_url = f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.text_converter = TextConverter()

    async def create_pg_vector_index_if_not_exists(self):
        # Establish an asynchronous connection to the database
        print("Inside create_pg_vector_index_if_not_exists")
        connection = await asyncpg.connect(
            host=self.db_host,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            port=self.db_port,
        )
        try:
            # Create an asynchronous cursor object to interact with the database
            async with connection.transaction():
                # Execute the alter table query
                await connection.execute(
                    "ALTER TABLE langchain_pg_embedding ALTER COLUMN embedding TYPE vector(1536)"
                )
                await connection.execute(
                    "CREATE INDEX IF NOT EXISTS langchain_embeddings_hnsw ON langchain_pg_embedding USING hnsw (embedding vector_cosine_ops)"
                )
        finally:
            # Close the connection
            await connection.close()

    async def index(self, indexer_input: IndexerInput):
        source_chunks = []
        counter = 0
        for file in indexer_input.files:
            file_path = os.path.join(os.environ["DOCUMENT_LOCAL_STORAGE_PATH"], file)
            print("file_path", file_path)
            content = await self.text_converter.textify(file_path)
            for chunk in self.splitter.split_text(content):
                new_metadata = {
                    "chunk-id": str(counter),
                    "document_name": file,
                }
                source_chunks.append(
                    Document(page_content=chunk, metadata=new_metadata)
                )
                counter += 1
        try:
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
            db = PGVector.from_documents(
                embedding=embeddings,
                documents=source_chunks,
                collection_name=indexer_input.collection_name,
                connection=self.db_url,
                pre_delete_collection=True,  # delete collection if it already exists
            )
            print(
                f"Embeddings have been created for the collection: {db.collection_name}"
            )
            await self.create_pg_vector_index_if_not_exists()
        except Exception as e:
            raise InternalServerException(e.__str__())


langchain_indexer = LangchainIndexer()
while True:
    message = consumer.receive_message(kafka_topic)
    print("Indexer Message:", message)
    data = json.loads(message)
    indexer_input = IndexerInput(**data)

    asyncio.run(langchain_indexer.index(indexer_input))
