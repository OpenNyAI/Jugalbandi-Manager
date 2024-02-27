from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta


class AzureStorageSync:
    def __init__(
        self, account_url: str, account_key: str, container_name: str, base_path: str
    ):
        self.account_url = account_url
        self.account_key = account_key
        self.container_name = container_name
        self.base_path = base_path
        self.client = BlobServiceClient(
            account_url=self.account_url, credential=self.account_key
        )

    def write_file(self, file_path: str, content: bytes, mime_type: str = None):
        blob_name = f"{self.base_path}{file_path}"
        blob_client = self.client.get_blob_client(self.container_name, blob_name)
        if mime_type is None:
            mime_type = (
                "audio/mpeg"
                if file_path.lower().endswith(".mp3")
                else "application/octet-stream"
            )
        content_settings = ContentSettings(content_type=mime_type)
        blob_client.upload_blob(
            content, overwrite=True, content_settings=content_settings
        )

    def make_public(self, file_path: str) -> str:
        blob_name = f"{self.base_path}{file_path}"
        blob_client = self.client.get_blob_client(self.container_name, blob_name)

        sas_token = generate_blob_sas(
            account_name=self.client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            start=datetime.utcnow() - timedelta(minutes=1),
            expiry=datetime.utcnow() + timedelta(days=30),
        )
        return f"{blob_client.url}?{sas_token}"
