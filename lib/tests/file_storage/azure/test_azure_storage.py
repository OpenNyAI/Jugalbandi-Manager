import os
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    ContentSettings,
    generate_blob_sas,
    BlobSasPermissions,
)

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)
from file_storage import AzureStorage


class TestAzureStorage:

    @patch("file_storage.azure.azure_storage.os.makedirs")
    @patch("file_storage.azure.azure_storage.os.getenv")
    @patch("azure.storage.blob.BlobServiceClient")
    def test_init(self, mock_blob_service_client, mock_getenv, mock_makedirs):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
            "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
            "AZURE_STORAGE_CONTAINER": "test_container",
        }.get(key, None)

        mock_blob_service_client_instance = MagicMock(spec=BlobServiceClient)
        mock_blob_service_client.return_value = mock_blob_service_client_instance

        storage = AzureStorage()
        assert storage.__client__ is not None
        mock_makedirs.assert_called_once_with("/tmp/jb_files", exist_ok=True)

        # Test missing account URL or key
        mock_getenv.side_effect = lambda key: (
            None
            if key == "AZURE_STORAGE_ACCOUNT_URL"
            else {
                "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
                "AZURE_STORAGE_CONTAINER": "test_container",
            }.get(key, None)
        )
        with pytest.raises(ValueError):
            AzureStorage()

        # Test missing container name
        mock_getenv.side_effect = lambda key: (
            None
            if key == "AZURE_STORAGE_CONTAINER"
            else {
                "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
                "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
            }.get(key, None)
        )
        with pytest.raises(ValueError):
            AzureStorage()

    @patch("azure.storage.blob.BlobClient")
    @patch("file_storage.azure.azure_storage.ContentSettings")
    @pytest.mark.asyncio
    async def test_write_file(self, mock_content_settings, mock_blob_client):
        with patch("file_storage.azure.azure_storage.os.getenv") as mock_getenv, patch(
            "file_storage.azure.azure_storage.BlobServiceClient"
        ) as mock_blob_service_client:
            mock_getenv.side_effect = lambda key: {
                "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
                "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
                "AZURE_STORAGE_CONTAINER": "test_container",
            }.get(key, None)

            mock_blob_service_client_instance = MagicMock(spec=BlobServiceClient)
            mock_blob_service_client.return_value = mock_blob_service_client_instance

            mock_blob_client_instance = MagicMock(spec=BlobClient)
            mock_blob_client_instance.upload_blob = AsyncMock()
            mock_blob_service_client_instance.get_blob_client.return_value = (
                mock_blob_client_instance
            )

            storage = AzureStorage()
            print("Writing file")

            await storage.write_file("test.txt", b"content")
            print("File written")

            mock_blob_service_client_instance.get_blob_client.assert_called_once_with(
                "test_container", "test.txt"
            )
            mock_blob_client_instance.upload_blob.assert_called_once_with(
                b"content", overwrite=True, content_settings=mock_content_settings()
            )

    @patch("azure.storage.blob.BlobClient")
    @pytest.mark.asyncio
    async def test_download_file_to_temp_storage(self, mock_blob_client):
        with patch("file_storage.azure.azure_storage.os.getenv") as mock_getenv, patch(
            "file_storage.azure.azure_storage.BlobServiceClient"
        ) as mock_blob_service_client:
            mock_getenv.side_effect = lambda key: {
                "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
                "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
                "AZURE_STORAGE_CONTAINER": "test_container",
            }.get(key, None)

            mock_blob_service_client_instance = MagicMock(spec=BlobServiceClient)
            mock_blob_service_client.return_value = mock_blob_service_client_instance
            storage = AzureStorage()

            mock_blob_client_instance = MagicMock(spec=BlobClient)
            mock_blob_client_instance.download_blob = AsyncMock()
            mock_blob_service_client_instance.get_blob_client.return_value = (
                mock_blob_client_instance
            )

            stream = MagicMock()
            stream.readall = AsyncMock(return_value=b"file content")
            mock_blob_client_instance.download_blob.return_value = stream

            file_path = await storage._download_file_to_temp_storage("test.txt")

            assert file_path == "/tmp/jb_files/test.txt"
            mock_blob_client_instance.download_blob.assert_called_once()
            stream.readall.assert_called_once()

    @patch("file_storage.azure.azure_storage.generate_blob_sas")
    @patch("azure.storage.blob.BlobClient")
    @pytest.mark.asyncio
    async def test_public_url(self, mock_blob_client, mock_generate_blob_sas):
        with patch("file_storage.azure.azure_storage.os.getenv") as mock_getenv, patch(
            "file_storage.azure.azure_storage.BlobServiceClient"
        ) as mock_blob_service_client:
            mock_getenv.side_effect = lambda key: {
                "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
                "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
                "AZURE_STORAGE_CONTAINER": "test_container",
            }.get(key, None)

            mock_blob_service_client_instance = MagicMock(spec=BlobServiceClient)
            mock_blob_service_client.return_value = mock_blob_service_client_instance
            storage = AzureStorage()

            mock_blob_client_instance = MagicMock(spec=BlobClient)
            mock_blob_client_instance.account_name = "test_account"
            mock_blob_client_instance.container_name = "test_container"
            mock_blob_service_client_instance.get_blob_client.return_value = (
                mock_blob_client_instance
            )
            mock_generate_blob_sas.return_value = "fake_sas_token"

            url = await storage.public_url("test.txt")

            assert "fake_sas_token" in url
            mock_blob_service_client_instance.get_blob_client.assert_called_once_with(
                "test_container", "test.txt"
            )
            mock_generate_blob_sas.assert_called_once()


if __name__ == "__main__":
    pytest.main()

# class TestAzureStorage:

#     @patch('file_storage.azure.azure_storage.os.makedirs')
#     @patch('file_storage.azure.azure_storage.os.getenv')
#     @patch('file_storage.azure.azure_storage.BlobServiceClient')
#     def test_init(self, mock_blob_service_client, mock_getenv, mock_makedirs):
#         # Mock environment variables
#         mock_getenv.side_effect = lambda key: {
#             "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
#             "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
#             "AZURE_STORAGE_CONTAINER": "test_container"
#         }.get(key, None)

#         storage = AzureStorage()
#         assert storage.__client__ is not None
#         mock_makedirs.assert_called_once_with("/tmp/jb_files", exist_ok=True)

#         # Test missing account URL or key
#         mock_getenv.side_effect = lambda key: None if key == "AZURE_STORAGE_ACCOUNT_URL" else {
#             "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
#             "AZURE_STORAGE_CONTAINER": "test_container"
#         }.get(key, None)
#         with pytest.raises(ValueError):
#             AzureStorage()

#         # Test missing container name
#         mock_getenv.side_effect = lambda key: None if key == "AZURE_STORAGE_CONTAINER" else {
#             "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
#             "AZURE_STORAGE_ACCOUNT_KEY": "fake_key"
#         }.get(key, None)
#         with pytest.raises(ValueError):
#             AzureStorage()

#     @patch('file_storage.azure.azure_storage.BlobClient')
#     @patch('file_storage.azure.azure_storage.AzureStorage.__client__.get_blob_client')
#     @patch('file_storage.azure.azure_storage.ContentSettings')
#     @pytest.mark.asyncio
#     async def test_write_file(self, mock_get_blob_client, mock_blob_client, mock_content_settings):
#         mock_blob_client.return_value = MagicMock(spec=BlobClient)
#         mock_get_blob_client.return_value = mock_blob_client

#         with patch('your_module.os.getenv') as mock_getenv:
#             mock_getenv.side_effect = lambda key: {
#                 "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
#                 "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
#                 "AZURE_STORAGE_CONTAINER": "test_container"
#             }.get(key, None)
#             storage = AzureStorage()

#         await storage.write_file("test.txt", b"content")

#         mock_get_blob_client.assert_called_once_with('test_container', 'test.txt')
#         mock_blob_client().upload_blob.assert_called_once_with(
#             b"content", overwrite=True, content_settings=mock_content_settings()
#         )

#     @patch('file_storage.azure.azure_storage.BlobClient')
#     @patch('file_storage.azure.azure_storage.AzureStorage.__client__.get_blob_client')
#     @pytest.mark.asyncio
#     async def test_download_file_to_temp_storage(self, mock_get_blob_client, mock_blob_client):
#         mock_blob_client.return_value = MagicMock(spec=BlobClient)
#         mock_get_blob_client.return_value = mock_blob_client

#         stream = MagicMock()
#         stream.readall = MagicMock(return_value=b"file content")
#         mock_blob_client().download_blob = MagicMock(return_value=stream)

#         with patch('your_module.os.getenv') as mock_getenv:
#             mock_getenv.side_effect = lambda key: {
#                 "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
#                 "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
#                 "AZURE_STORAGE_CONTAINER": "test_container"
#             }.get(key, None)
#             storage = AzureStorage()

#         file_path = await storage._download_file_to_temp_storage("test.txt")

#         assert file_path == "/tmp/jb_files/test.txt"
#         mock_blob_client().download_blob.assert_called_once()
#         stream.readall.assert_called_once()

#     @patch('file_storage.azure.azure_storage.generate_blob_sas')
#     @patch('file_storage.azure.azure_storage.BlobClient')
#     @patch('file_storage.azure.azure_storage.AzureStorage.__client__.get_blob_client')
#     def test_public_url(self, mock_get_blob_client, mock_blob_client, mock_generate_blob_sas):
#         mock_blob_client.return_value = MagicMock(spec=BlobClient)
#         mock_get_blob_client.return_value = mock_blob_client
#         mock_generate_blob_sas.return_value = "fake_sas_token"

#         with patch('your_module.os.getenv') as mock_getenv:
#             mock_getenv.side_effect = lambda key: {
#                 "AZURE_STORAGE_ACCOUNT_URL": "https://example.blob.core.windows.net",
#                 "AZURE_STORAGE_ACCOUNT_KEY": "fake_key",
#                 "AZURE_STORAGE_CONTAINER": "test_container"
#             }.get(key, None)
#             storage = AzureStorage()

#         url = storage.public_url("test.txt")

#         assert "fake_sas_token" in url
#         mock_get_blob_client.assert_called_once_with('test_container', 'test.txt')
#         mock_generate_blob_sas.assert_called_once()

# if __name__ == '__main__':
#     pytest.main()
