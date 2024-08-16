import unittest.mock as mock
import pytest
from gcloud.aio.storage import Storage, Blob
from lib.file_storage import GCPAsyncStorage
import aiohttp

class TestGCPAsyncStorage:

    @mock.patch("lib.file_storage.gcp.gcp_storage.os.makedirs")
    @mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv")
    @mock.patch("gcloud.aio.storage.Storage")
    @pytest.mark.asyncio
    async def test_init(self, mock_storage, mock_getenv, mock_makedirs):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            "GCP_BUCKET_NAME": "test_bucket"
        }.get(key, None)

        mock_storage_instance = mock.MagicMock(spec=Storage)
        mock_storage.return_value = mock_storage_instance

        storage = GCPAsyncStorage()
        assert storage.__client__ is not None
        mock_makedirs.assert_called_once_with("/tmp/jb_files", exist_ok=True)

        # Test missing bucket name
        mock_getenv.side_effect = lambda key: None if key == "GCP_BUCKET_NAME" else "value"
        with pytest.raises(ValueError):
            GCPAsyncStorage()

    @pytest.mark.asyncio
    async def test_write_file(self):
        with mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv") as mock_getenv, \
             mock.patch("gcloud.aio.storage.Storage") as mock_storage:
            mock_getenv.side_effect = lambda key: {
                "GCP_BUCKET_NAME": "test_bucket"
            }.get(key, None)

            mock_storage_instance = mock.MagicMock(spec=Storage)
            mock_storage_instance.upload = mock.AsyncMock()
            mock_storage.return_value = mock_storage_instance

            storage = GCPAsyncStorage()

            await storage.write_file("test.txt", b"content")
            mock_storage_instance.upload.assert_called_once_with(
                "test_bucket", "test.txt", b"content", content_type="application/octet-stream"
            )

    @pytest.mark.asyncio
    async def test_download_file_to_temp_storage(self):
        with mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv") as mock_getenv, \
             mock.patch("gcloud.aio.storage.Storage") as mock_storage:
            mock_getenv.side_effect = lambda key: {
                "GCP_BUCKET_NAME": "test_bucket"
            }.get(key, None)

            mock_storage_instance = mock.MagicMock(spec=Storage)
            mock_storage_instance.download_to_filename = mock.AsyncMock()
            mock_storage.return_value = mock_storage_instance

            storage = GCPAsyncStorage()

            file_path = await storage._download_file_to_temp_storage("test.txt")
            assert file_path == "/tmp/jb_files/test.txt"
            mock_storage_instance.download_to_filename.assert_called_once_with(
                "test_bucket", "test.txt", "/tmp/jb_files/test.txt"
            )

    @pytest.mark.asyncio
    @mock.patch("lib.file_storage.gcp.gcp_storage.Blob")
    @mock.patch("lib.file_storage.gcp.gcp_storage.Storage")
    @mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv")
    async def test_public_url(self, mock_getenv, mock_storage, mock_blob):
        mock_getenv.side_effect = lambda key: {
            "GCP_BUCKET_NAME": "test_bucket"
        }.get(key, None)

        mock_blob_instance = mock.MagicMock(spec=Blob)
        mock_blob_instance.get_signed_url = mock.AsyncMock(return_value="http://example.com/signed_url")
        mock_blob.return_value = mock_blob_instance

        mock_storage_instance = mock.MagicMock(spec=Storage)
        mock_storage.return_value = mock_storage_instance

        storage = GCPAsyncStorage()

        url = await storage.public_url("test.txt")
        assert url == "http://example.com/signed_url"
        mock_blob_instance.get_signed_url.assert_called_once_with(
            expiration=86400
        )

if __name__ == "__main__":
    pytest.main()