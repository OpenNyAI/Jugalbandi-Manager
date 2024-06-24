from unittest.mock import patch, mock_open
import pytest
from lib.file_storage import LocalStorage


class TestLocalStorage:
    tmp_folder = "/tmp/jb_files"
    LocalStorage.tmp_folder = tmp_folder

    @patch("lib.file_storage.local.local_storage.os.makedirs")
    @patch("lib.file_storage.local.local_storage.os.getenv")
    def test_init(self, mock_getenv, mock_makedirs):
        # Test with PUBLIC_URL_PREFIX set
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        assert storage.public_url_prefix == "http://example.com"
        mock_makedirs.assert_called_once_with(self.tmp_folder, exist_ok=True)

        # Test without PUBLIC_URL_PREFIX set
        mock_getenv.return_value = None
        with pytest.raises(ValueError):
            LocalStorage()

    @patch("lib.file_storage.local.local_storage.open", new_callable=mock_open)
    @patch("lib.file_storage.local.local_storage.os.getenv")
    @pytest.mark.asyncio
    async def test_write_file_str(self, mock_getenv, mock_open):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        await storage.write_file("test.txt", "content")
        mock_open.assert_called_once_with(f"{self.tmp_folder}/test.txt", mode="w")
        mock_open().write.assert_called_once_with("content")

    @patch("lib.file_storage.local.local_storage.open", new_callable=mock_open)
    @patch("lib.file_storage.local.local_storage.os.getenv")
    @pytest.mark.asyncio
    async def test_write_file_bytes(self, mock_getenv, mock_open):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        await storage.write_file("test.bin", b"content")
        mock_open.assert_called_once_with(f"{self.tmp_folder}/test.bin", mode="wb")
        mock_open().write.assert_called_once_with(b"content")

    @patch("lib.file_storage.local.local_storage.os.getenv")
    @pytest.mark.asyncio
    async def test_write_file_invalid(self, mock_getenv):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        with pytest.raises(TypeError):
            await storage.write_file("test.txt", 123)

    @patch("lib.file_storage.local.local_storage.os.getenv")
    @pytest.mark.asyncio
    async def test_download_file_to_temp_storage(self, mock_getenv):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        file_path = await storage._download_file_to_temp_storage("test.txt")
        assert file_path == f"{self.tmp_folder}/test.txt"

    @patch("lib.file_storage.local.local_storage.os.getenv")
    @pytest.mark.asyncio
    async def test_public_url(self, mock_getenv):
        mock_getenv.return_value = "http://example.com"
        storage = LocalStorage()
        url = await storage.public_url("test.txt")
        assert url == "http://example.com/test.txt"

        storage.public_url_prefix = None
        with pytest.raises(ValueError):
            await storage.public_url("test.txt")


if __name__ == "__main__":
    pytest.main()
