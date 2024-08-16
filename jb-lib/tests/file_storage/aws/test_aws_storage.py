from unittest.mock import patch, MagicMock, AsyncMock
import pytest
import aioboto3
from lib.file_storage import AWSAsyncStorage


class TestAWSAsyncStorage:

    @patch("lib.file_storage.aws.aws_storage.os.makedirs")
    @patch("lib.file_storage.aws.aws_storage.os.getenv")
    @patch("aioboto3.client")
    def test_init(self, mock_aioboto3_client, mock_getenv, mock_makedirs):
        # Mock environment variables
        mock_getenv.side_effect = lambda key: {
            "AWS_ACCESS_KEY_ID": "fake_access_key",
            "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
            "AWS_REGION": "us-east-1",
            "AWS_S3_BUCKET_NAME": "test_bucket",
        }.get(key, None)

        mock_aioboto3_client_instance = MagicMock(spec=aioboto3.client)
        mock_aioboto3_client.return_value = mock_aioboto3_client_instance

        storage = AWSAsyncStorage()
        assert storage.__client__ is not None
        mock_makedirs.assert_called_once_with("/tmp/jb_files", exist_ok=True)

        # Test missing AWS credentials or region
        mock_getenv.side_effect = lambda key: (
            None
            if key == "AWS_ACCESS_KEY_ID"
            else {
                "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
                "AWS_REGION": "us-east-1",
                "AWS_S3_BUCKET_NAME": "test_bucket",
            }.get(key, None)
        )
        with pytest.raises(ValueError):
            AWSAsyncStorage()

        # Test missing bucket name
        mock_getenv.side_effect = lambda key: (
            None
            if key == "AWS_S3_BUCKET_NAME"
            else {
                "AWS_ACCESS_KEY_ID": "fake_access_key",
                "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
                "AWS_REGION": "us-east-1",
            }.get(key, None)
        )
        with pytest.raises(ValueError):
            AWSAsyncStorage()

    @patch("aioboto3.client")
    @pytest.mark.asyncio
    async def test_write_file(self):
        with patch("lib.file_storage.aws.aws_storage.os.getenv") as mock_getenv, patch("aioboto3.client") as mock_aioboto3_client:
            mock_getenv.side_effect = lambda key: {
                "AWS_ACCESS_KEY_ID": "fake_access_key",
                "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
                "AWS_REGION": "us-east-1",
                "AWS_S3_BUCKET_NAME": "test_bucket",
            }.get(key, None)

            mock_aioboto3_client_instance = MagicMock(spec=aioboto3.client)
            mock_aioboto3_client_instance.put_object = AsyncMock()
            mock_aioboto3_client.return_value = mock_aioboto3_client_instance

            storage = AWSAsyncStorage()
            await storage.write_file("test.txt", b"content")

            mock_aioboto3_client_instance.put_object.assert_called_once_with(
                Bucket="test_bucket",
                Key="test.txt",
                Body=b"content",
                ContentType="application/octet-stream",
            )

    @patch("aioboto3.client")
    @pytest.mark.asyncio
    async def test_download_file_to_temp_storage(self):
        with patch("lib.file_storage.aws.aws_storage.os.getenv") as mock_getenv, patch("aioboto3.client") as mock_aioboto3_client:
            mock_getenv.side_effect = lambda key: {
                "AWS_ACCESS_KEY_ID": "fake_access_key",
                "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
                "AWS_REGION": "us-east-1",
                "AWS_S3_BUCKET_NAME": "test_bucket",
            }.get(key, None)

            mock_aioboto3_client_instance = MagicMock(spec=aioboto3.client)
            mock_aioboto3_client_instance.get_object = AsyncMock()

            stream = MagicMock()
            stream.iter_chunks = AsyncMock(return_value=[b"file content"])
            mock_aioboto3_client_instance.get_object.return_value = {"Body": stream}
            mock_aioboto3_client.return_value = mock_aioboto3_client_instance

            storage = AWSAsyncStorage()
            file_path = await storage._download_file_to_temp_storage("test.txt")

            assert file_path == "/tmp/jb_files/test.txt"
            mock_aioboto3_client_instance.get_object.assert_called_once_with(
                Bucket="test_bucket", Key="test.txt"
            )
            stream.iter_chunks.assert_called_once()
    
    @patch("aioboto3.client")
    @pytest.mark.asyncio
    async def test_public_url(self):
        with patch("lib.file_storage.aws.aws_storage.os.getenv") as mock_getenv, patch("aioboto3.client") as mock_aioboto3_client:
            mock_getenv.side_effect = lambda key: {
                "AWS_ACCESS_KEY_ID": "fake_access_key",
                "AWS_SECRET_ACCESS_KEY": "fake_secret_key",
                "AWS_REGION": "us-east-1",
                "AWS_S3_BUCKET_NAME": "test_bucket",
            }.get(key, None)

            mock_aioboto3_client_instance = MagicMock(spec=aioboto3.client)
            mock_aioboto3_client_instance.generate_presigned_url = AsyncMock(
                return_value="https://test_bucket.s3.amazonaws.com/test.txt?fake_presigned_url"
            )
            mock_aioboto3_client.return_value = mock_aioboto3_client_instance

            storage = AWSAsyncStorage()
            url = await storage.public_url("test.txt")

            assert "fake_presigned_url" in url
            mock_aioboto3_client_instance.generate_presigned_url.assert_called_once_with(
                ClientMethod='get_object',
                Params={'Bucket': "test_bucket", 'Key': "test.txt"},
                ExpiresIn=3600 * 24,
            )


if __name__ == "__main__":
    pytest.main()
