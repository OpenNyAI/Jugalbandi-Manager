import base64
from enum import Enum
from typing import List
from fastapi.datastructures import UploadFile
from pydantic import BaseModel


class IndexType(str, Enum):
    default = "default"
    r2r = "r2r"


class SerializableUploadFile(BaseModel):
    filename: str
    file_content: str
    content_type: str

    @classmethod
    def from_upload_file(cls, upload_file: UploadFile):
        content = base64.b64encode(upload_file.file.read()).decode("utf-8")
        return cls(
            filename=upload_file.filename,
            file_content=content,
            content_type=upload_file.content_type,
        )

    def to_bytes(self) -> bytes:
        return base64.b64decode(self.file_content)


class Indexer(BaseModel):
    type: str
    collection_name: str
    files: List[SerializableUploadFile]
