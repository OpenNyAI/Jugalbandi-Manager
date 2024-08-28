import os
from dotenv import load_dotenv
from typing import Union, Optional
import logging
from gcloud.aio.storage import Storage, Blob
from ..storage import AsyncStorage

load_dotenv()

logger = logging.getLogger("storage")
class GCPAsyncStorage(AsyncStorage):
    __client__ = None
    tmp_folder = "/tmp/jb_files"

    def __init__(self):
        logger.info("Initializing GCP Storage")
        bucket_name = os.getenv("GCP_BUCKET_NAME")
        if not bucket_name:
            raise ValueError(
                "GCPAsyncStorage client not initialized. Missing bucket_name "
            )
        self.__bucket_name__ = bucket_name
        self.__client__ = Storage()
        os.makedirs(self.tmp_folder, exist_ok=True)

    async def write_file(
        self,
        file_path: str,
        file_content: Union[str, bytes],
        mime_type: Optional[str] = None,
    ):
        if not self.__client__:
            raise Exception("GCPAsyncStorage client not initialized")

        if mime_type is None:
            mime_type = (
                "audio/mpeg"
                if file_path.lower().endswith(".mp3")
                else "application/octet-stream"
            )
        await self.__client__.upload(
            self.__bucket_name__, file_path, file_content, content_type=mime_type
        )

    async def _download_file_to_temp_storage(
        self, file_path: Union[str, os.PathLike]
    ) -> Union[str, os.PathLike]:
        if not self.__client__:
            raise Exception("GCPAsyncStorage client not initialized")

        tmp_file_path = os.path.join(self.tmp_folder, file_path)
        await self.__client__.download_to_filename(
            self.__bucket_name__, file_path, tmp_file_path
        )

        return tmp_file_path

    async def public_url(self, file_path: str) -> str:
        if not self.__client__:
            raise Exception("GCPAsyncStorage client not initialized")

        blob = Blob(self.__bucket_name__, file_path, metadata={})
        url = await blob.get_signed_url(
            expiration=86400,  # 1 day
        )
        return url
