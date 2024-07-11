import os
import logging
from typing import Union, Optional
from ..storage import AsyncStorage

logger = logging.getLogger("storage")


class LocalAsyncStorage(AsyncStorage):
    tmp_folder = "/mnt/jb_files"

    def __init__(self):
        self.public_url_prefix = os.getenv("PUBLIC_URL_PREFIX")
        logger.info("Initializing Local Storage")
        if not self.public_url_prefix:
            logger.error("PUBLIC_URL_PREFIX not set")
            raise ValueError("PUBLIC_URL_PREFIX not set")
        os.makedirs(self.tmp_folder, exist_ok=True)

    async def write_file(
        self,
        file_path: str,
        file_content: Union[str, bytes],
        mime_type: Optional[str] = None,
    ):
        if isinstance(file_content, str):
            mode = "w"
        elif isinstance(file_content, bytes):
            mode = "wb"
        else:
            raise TypeError("file_content must be either str or bytes")
        with open(os.path.join(self.tmp_folder, file_path), mode=mode) as fp:
            fp.write(file_content)

    async def _download_file_to_temp_storage(
        self, file_path: Union[str, os.PathLike]
    ) -> Union[str, os.PathLike]:
        return os.path.join(self.tmp_folder, file_path)

    async def public_url(self, file_path: str) -> str:
        if self.public_url_prefix:
            return f"{self.public_url_prefix}/{file_path}"
        else:
            raise ValueError("PUBLIC_URL_PREFIX not set")
