from unittest.mock import patch, MagicMock
import pytest
from datetime import timedelta
from google.cloud import storage
from lib.file_storage import GCPAsyncStorage

class TestGCPAsyncStorage:

    @patch("lib.file_storage.gcp.gcp_storage.os.makedirs")
    @patch("lib.file_storage.gcp.gcp_storage.os.getenv")
    @patch("google.cloud.storage.Client")
    def test_init(self, mock_storage_client, mock_getenv, mock_makedirs):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            "GCP_BUCKET_NAME": "test_bucket"
        }.get(key, None)

        mock_storage_client_instance = MagicMock(spec=storage.Client)
        mock_storage_client.return_value = mock_storage_client_instance

        storage = GCPAsyncStorage()
        assert storage.__client__ is not None
        mock_makedirs.assert_called_once_with("/tmp/jb_files", exist_ok=True)

        # Test missing bucket name
        mock_getenv.side_effect = lambda key: (
            None if key == "GCP_BUCKET_NAME" else "test_value"
        )
        with pytest.raises(ValueError):
            GCPAsyncStorage()

    @pytest.mark.asyncio
    async def test_write_file(self):
        with patch("lib.file_storage.gcp.gcp_storage.os.getenv") as mock_getenv, patch("google.cloud.storage.Client") as mock_storage_client:
            mock_getenv.side_effect = lambda key: {
                "GCP_BUCKET_NAME": "test_bucket"
            }.get(key, None)

            mock_storage_client_instance = MagicMock(spec=storage.Client)
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_storage_client_instance.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.upload_from_string = MagicMock()

            storage = GCPAsyncStorage()

            await storage.write_file("test.txt", b"content")
            
            mock_bucket.blob.assert_called_once_with("test.txt")
            mock_blob.upload_from_string.assert_called_once_with(b"content", content_type="application/octet-stream")

    @pytest.mark.asyncio
    async def test_download_file_to_temp_storage(self):
        with patch("lib.file_storage.gcp.gcp_storage.os.getenv") as mock_getenv, patch("google.cloud.storage.Client") as mock_storage_client:
            mock_getenv.side_effect = lambda key: {
                "GCP_BUCKET_NAME": "test_bucket"
            }.get(key, None)

            mock_storage_client_instance = MagicMock(spec=storage.Client)
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_storage_client_instance.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.download_to_filename = MagicMock()

            storage = GCPAsyncStorage()

            tmp_file_path = await storage._download_file_to_temp_storage("test.txt")
            
            assert tmp_file_path == "/tmp/jb_files/test.txt"
            mock_bucket.blob.assert_called_once_with("test.txt")
            mock_blob.download_to_filename.assert_called_once_with("/tmp/jb_files/test.txt")

    @pytest.mark.asyncio
    async def test_public_url(self):
        with patch("lib.file_storage.gcp.gcp_storage.os.getenv") as mock_getenv, patch("google.cloud.storage.Client") as mock_storage_client:
            mock_getenv.side_effect = lambda key: {
                "GCP_BUCKET_NAME": "test_bucket"
            }.get(key, None)

            mock_storage_client_instance = MagicMock(spec=storage.Client)
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            mock_storage_client_instance.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.generate_signed_url = MagicMock(return_value="http://example.com/signed_url")

            storage = GCPAsyncStorage()

            url = await storage.public_url("test.txt")
            
            assert url == "http://example.com/signed_url"
            mock_bucket.blob.assert_called_once_with("test.txt")
            mock_blob.generate_signed_url.assert_called_once_with(expiration=timedelta(days=1))

if __name__ == "__main__":
    pytest.main()
