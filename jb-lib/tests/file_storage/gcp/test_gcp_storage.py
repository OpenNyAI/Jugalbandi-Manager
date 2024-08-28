import unittest.mock as mock
import pytest
from gcloud.aio.storage import Storage, Blob
from lib.file_storage.gcp.gcp_storage import GCPAsyncStorage

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

        mock_getenv.side_effect = lambda key: None if key == "GCP_BUCKET_NAME" else "value"
        with pytest.raises(ValueError):
            GCPAsyncStorage()

@pytest.mark.asyncio
@mock.patch("lib.file_storage.gcp.gcp_storage.GCPAsyncStorage.write_file", new_callable=mock.AsyncMock)
@mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv")
async def test_write_file(mock_getenv, mock_write_file):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test_bucket"
    }.get(key, None)

    mock_write_file.return_value = 0

    storage = GCPAsyncStorage()
    result = await storage.write_file("some_bucket", "some_file", b"some_data")
    
    mock_write_file.assert_called_once_with("some_bucket", "some_file", b"some_data")
    
    assert result == 0

@pytest.mark.asyncio
@mock.patch("lib.file_storage.gcp.gcp_storage.GCPAsyncStorage._download_file_to_temp_storage", new_callable=mock.AsyncMock)
@mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv")
async def test_download_file_to_temp_storage(mock_getenv, mock_download):
    mock_getenv.side_effect = lambda key: {
        "GCP_BUCKET_NAME": "test_bucket"
    }.get(key, None)

    mock_download.return_value = 0 

    storage = GCPAsyncStorage()
    result = await storage._download_file_to_temp_storage("some_bucket", "some_file")
    
    mock_download.assert_called_once_with("some_bucket", "some_file")
    
    assert result == 0  

@pytest.mark.asyncio
@mock.patch("lib.file_storage.gcp.gcp_storage.Storage")
@mock.patch("lib.file_storage.gcp.gcp_storage.Blob")
@mock.patch("lib.file_storage.gcp.gcp_storage.os.getenv")
async def test_public_url(mock_getenv, mock_blob, mock_storage):
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
    mock_blob_instance.get_signed_url.assert_called_once_with(expiration=86400)

if __name__ == "__main__":
    pytest.main()
