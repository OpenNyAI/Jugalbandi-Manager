import json
import os
from contextlib import asynccontextmanager
from unittest.mock import ANY, AsyncMock, MagicMock, mock_open, patch

import pytest
from lib.data_models import Indexer


# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("POSTGRES_DATABASE_NAME", "test_db")
    monkeypatch.setenv("POSTGRES_DATABASE_USERNAME", "test_user")
    monkeypatch.setenv("POSTGRES_DATABASE_PASSWORD", "test_password")
    monkeypatch.setenv("POSTGRES_DATABASE_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_DATABASE_PORT", "5432")


# Mock read_file function
@asynccontextmanager
async def mock_read_file(file_path, mode):
    mock_file = MagicMock()
    mock_file.read = AsyncMock(return_value=b"test content")
    mock_file.name = "temp_test.txt"
    yield mock_file


# Mock storage instance
mock_storage_instance = MagicMock()
mock_storage_instance.read_file = mock_read_file


# Patching the StorageHandler in lib.file_storage with the mock
with patch(
    "lib.file_storage.StorageHandler.get_async_instance",
    return_value=mock_storage_instance,
):
    import indexing

    def test_docx_parser():
        with patch("docx2txt.process", return_value="DOCX Content") as mock_process:
            result = indexing.docx_parser("test.docx")
            assert result == "DOCX Content"
            mock_process.assert_called_once_with("test.docx")

    def test_pdf_parser():
        mock_page = MagicMock()
        mock_page.get_text.return_value = "PDF Page Content"
        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = iter([mock_page])
        with patch("fitz.open", return_value=mock_doc):
            result = indexing.pdf_parser("test.pdf")
            assert result == "PDF Page Content"

    def test_xlsx_parser():
        mock_df = MagicMock()
        mock_df.to_string.return_value = "XLSX Content"
        with patch("pandas.read_excel", return_value=mock_df):
            result = indexing.xlsx_parser("test.xlsx")
            assert result == "XLSX Content"
            mock_df.to_string.assert_called_once_with(index=False)

    def test_json_parser():
        mock_json_data = {"key": "value"}
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_json_data))):
            result = indexing.json_parser("test.json")
            assert result == json.dumps(mock_json_data, indent=4)

    def test_default_parser():
        with patch("builtins.open", mock_open(read_data="Default Content")):
            result = indexing.default_parser("test.txt")
            assert result == "Default Content"

    # Test TextConverter.textify method
    @pytest.mark.asyncio
    async def test_text_converter_textify():
        converter = indexing.TextConverter()
        with patch("indexing.parse_file", return_value="Parsed Content"):
            result = await converter.textify("test.txt")
            assert result == "Parsed Content"

    # Test DataIndexer.index method for default input
    @pytest.mark.asyncio
    async def test_default_data_indexer():
        indexer = indexing.DataIndexer()
        indexer_input = Indexer(
            files=["test.txt"],
            collection_name="test_collection",
            type="default",
            chunk_size=2000,
            chunk_overlap=100,
        )
        with patch.object(
            indexer.text_converter,
            "textify",
            AsyncMock(return_value="File Content"),
        ), patch.object(
            indexer, "get_embeddings", AsyncMock()
        ), patch.object(
            indexer, "create_pg_vector_index_if_not_exists", AsyncMock()
        ), patch(
            "langchain_community.vectorstores.PGVector.from_documents", MagicMock()
        ) as mock_pg_vector:
            await indexer.index(indexer_input)
            mock_pg_vector.assert_called_once()
            indexer.create_pg_vector_index_if_not_exists.assert_awaited_once()

    # Test DataIndexer.index method for r2r input
    @pytest.mark.asyncio
    async def test_r2r_data_indexer():
        indexer = indexing.DataIndexer()
        indexer_input = Indexer(
            files=["test.txt"],
            collection_name="test_collection",
            type="r2r",
            chunk_size=4000,
            chunk_overlap=200,
        )
        mock_r2r_app = MagicMock()
        mock_r2r_app.engine.aingest_files = AsyncMock()

        with patch.object(indexer, "get_r2r", return_value=mock_r2r_app):
            await indexer.index(indexer_input)
            mock_r2r_app.engine.aingest_files.assert_awaited_once_with(files=[ANY])
            assert os.environ["POSTGRES_VECS_COLLECTION"] == "test_collection"
