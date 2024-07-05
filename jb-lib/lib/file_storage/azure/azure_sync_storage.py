import os
from typing import Union, Optional
from datetime import datetime, timedelta, timezone
import logging
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions, ContentSettings
from ..storage import SyncStorage

logger = logging.getLogger("storage")


class AzureSyncStorage(SyncStorage):
    __client__ = None
    tmp_folder = "/tmp/jb_files"

    def __init__(self):
        logger.info("Initializing Azure Storage")
        account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
        account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        if not account_key or not account_url:
            raise ValueError(
                "AzureSyncStorage client not initialized. Missing account_url or account_key"
            )
        self.__account_key__ = account_key
        self.__container_name__ = os.getenv("AZURE_STORAGE_CONTAINER")
        if not self.__container_name__:
            raise ValueError(
                "AzureSyncStorage client not initialized. Missing container_name"
            )
        self.__client__ = BlobServiceClient(
            account_url=account_url, credential=account_key
        )
        os.makedirs(self.tmp_folder, exist_ok=True)

    def write_file(
        self,
        file_path: str,
        file_content: Union[str, bytes],
        mime_type: Optional[str] = None,
    ):
        if not self.__client__:
            raise Exception("AzureSyncStorage client not initialized")

        blob_name = f"{file_path}"
        blob_client = self.__client__.get_blob_client(
            self.__container_name__, blob_name
        )
        if mime_type is None:
            mime_type = (
                "audio/mpeg"
                if file_path.lower().endswith(".mp3")
                else "application/octet-stream"
            )
        content_settings = ContentSettings(content_type=mime_type)
        blob_client.upload_blob(
            file_content, overwrite=True, content_settings=content_settings
        )

    def _download_file_to_temp_storage(
        self, file_path: Union[str, os.PathLike]
    ) -> Union[str, os.PathLike]:
        if not self.__client__:
            raise Exception("AzureSyncStorage client not initialized")
        blob_name = f"{file_path}"
        blob_client = self.__client__.get_blob_client(
            self.__container_name__, blob_name
        )

        tmp_file_path = os.path.join(self.tmp_folder, file_path)
        with open(tmp_file_path, "wb") as my_blob:
            stream = blob_client.download_blob()
            data = stream.readall()
            my_blob.write(data)
        return tmp_file_path

    def public_url(self, file_path: str) -> str:
        if not self.__client__:
            raise Exception("AzureSyncStorage client not initialized")

        blob_name = f"{file_path}"
        blob_client = self.__client__.get_blob_client(
            self.__container_name__, blob_name
        )

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(days=1)

        sas_token = generate_blob_sas(
            account_name=blob_client.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_name,
            account_key=self.__account_key__,
            permission=BlobSasPermissions(read=True),
            start=start_time,
            expiry=expiry_time,
        )
        return f"{blob_client.url}?{sas_token}"
