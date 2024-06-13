import os
import sys
import pytest
import asyncio
from unittest.mock import patch, mock_open
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from file_storage import LocalStorage 

class TestLocalStorage:

    @patch('file_storage.local.local_storage.os.makedirs')
    @patch('file_storage.local.local_storage.os.getenv')
    def test_init(self, mock_getenv, mock_makedirs):
        # Test with PUBLIC_URL_PREFIX set
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        assert storage.public_url_prefix == "http://example.com"
        mock_makedirs.assert_called_once_with("/mnt/jb_files", exist_ok=True)

        # Test without PUBLIC_URL_PREFIX set
        mock_getenv.return_value = None
        with pytest.raises(ValueError):
            LocalStorage()

    @patch('file_storage.local.local_storage.open', new_callable=mock_open)
    @patch('file_storage.local.local_storage.os.getenv')
    @pytest.mark.asyncio
    async def test_write_file_str(self, mock_getenv, mock_open):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        await storage.write_file("test.txt", "content")
        mock_open.assert_called_once_with("/mnt/jb_files/test.txt", mode="w")
        mock_open().write.assert_called_once_with("content")

    @patch('file_storage.local.local_storage.open', new_callable=mock_open)
    @patch('file_storage.local.local_storage.os.getenv')
    @pytest.mark.asyncio
    async def test_write_file_bytes(self, mock_getenv, mock_open):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        await storage.write_file("test.bin", b'content')
        mock_open.assert_called_once_with("/mnt/jb_files/test.bin", mode="wb")
        mock_open().write.assert_called_once_with(b'content')

    @patch('file_storage.local.local_storage.os.getenv')
    @pytest.mark.asyncio
    async def test_write_file_invalid(self, mock_getenv):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        with pytest.raises(TypeError):
            await storage.write_file("test.txt", 123)

    @patch('file_storage.local.local_storage.os.getenv')
    @pytest.mark.asyncio
    async def test_download_file_to_temp_storage(self, mock_getenv):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        file_path = await storage._download_file_to_temp_storage("test.txt")
        assert file_path == "/mnt/jb_files/test.txt"

    @patch('file_storage.local.local_storage.os.getenv')
    @pytest.mark.asyncio
    async def test_public_url(self, mock_getenv):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        url = await storage.public_url("test.txt")
        assert url == "http://example.com/test.txt"

        storage.public_url_prefix = None
        with pytest.raises(ValueError):
            await storage.public_url("test.txt")

if __name__ == '__main__':
    pytest.main()