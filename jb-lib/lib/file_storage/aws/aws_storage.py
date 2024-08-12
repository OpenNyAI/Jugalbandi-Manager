import os
from typing import Union, Optional
from datetime import datetime, timedelta, timezone
import logging
import aioboto3
from ..storage import AsyncStorage

logger = logging.getLogger("storage")


class AWSAsyncStorage(AsyncStorage):
    __client__ = None
    tmp_folder = "/tmp/jb_files"

    def __init__(self):
        logger.info("Initializing AWS Storage")
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region_name = os.getenv("AWS_REGION")

        if not aws_access_key or not aws_secret_key or not aws_region_name:
            raise ValueError(
                "AWSAsyncStorage client not initialized. Missing AWS credentials or region"
            )
        self.__bucket_name__ = os.getenv("AWS_S3_BUCKET_NAME")
        if not self.__bucket_name__:
            raise ValueError(
                "AWSAsyncStorage client not initialized. Missing bucket_name"
            )

        self.__client__ = aioboto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region_name,
        )
        os.makedirs(self.tmp_folder, exist_ok=True)

    async def write_file(
        self,
        file_path: str,
        file_content: Union[str, bytes],
        mime_type: Optional[str] = None,
    ):
        if not self.__client__:
            raise Exception("AWSAsyncStorage client not initialized")

        if mime_type is None:
            mime_type = (
                "audio/mpeg"
                if file_path.lower().endswith(".mp3")
                else "application/octet-stream"
            )
        await self.__client__.put_object(
            Bucket=self.__bucket_name__,
            Key=file_path,
            Body=file_content,
            ContentType=mime_type,
        )

    async def _download_file_to_temp_storage(
        self, file_path: Union[str, os.PathLike]
    ) -> Union[str, os.PathLike]:
        if not self.__client__:
            raise Exception("AWSAsyncStorage client not initialized")

        tmp_file_path = os.path.join(self.tmp_folder, file_path)
        with open(tmp_file_path, "wb") as f:
            response = await self.__client__.get_object(Bucket=self.__bucket_name__, Key=file_path)
            async for chunk in response["Body"].iter_chunks():
                f.write(chunk)        
        return tmp_file_path

    async def public_url(self, file_path: str) -> str:
        if not self.__client__:
            raise Exception("AWSAsyncStorage client not initialized")

        url = await self.__client__.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': self.__bucket_name__, 'Key': file_path},
            ExpiresIn=3600*24  #1 day
        )
        return url

