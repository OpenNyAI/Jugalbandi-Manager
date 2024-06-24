import asyncio
from enum import Enum
from io import BytesIO
from typing import Any, AsyncIterator, Dict, List, Protocol
import os
import uuid
import re
import logging
from pydantic import BaseModel
from zipfile import ZipFile, ZipInfo
from .storage import Storage

logger = logging.getLogger(__name__)


class AsyncReader(Protocol):
    async def read(self) -> bytes:
        pass


class WrapSyncReader:
    def __init__(self, file_like: Any):
        self.file_like = file_like

    async def read(self) -> bytes:
        return self.file_like.read()


class DocumentSourceFile:
    def __init__(self, filename: str, reader: AsyncReader):
        self._filename = filename
        self.reader = reader

    def filename(self) -> str:
        return self._filename

    def read_content(self):
        return self.reader.read()


class ZipFileReader:
    def __init__(self, zf: ZipFile, fileinfo: ZipInfo):
        self.zf = zf
        self.fileinfo = fileinfo

    async def read(self) -> bytes:
        return self.zf.read(self.fileinfo)


class DocumentFormat(Enum):
    DEFAULT = ""
    TEXT = "txt"


class DataFileInfo(BaseModel):
    default_file_name: str
    extensions: List[str]


INDEX_FILE_REGEX = re.compile(r"^index\..*")


class DocumentCollection:
    def __init__(
        self,
        collection_id: str,
        local_store: Storage,
        remote_store: Storage,
    ):
        self._id = collection_id
        self.local_store = local_store
        self.remote_store = remote_store
        self.data_files: Dict[str, DataFileInfo] = {}
        self.index_files: Dict[str, List[str]] = {}
        self.dir: List[str] = []

    @property
    def id(self):
        return self._id

    def _collection_path(self):
        return self.local_store.path(self._id)

    @staticmethod
    def _is_index_file(file_path: str):
        basename = os.path.basename(file_path)
        return INDEX_FILE_REGEX.match(basename) is not None

    def _filename(
        self, file_suffix: str, format: DocumentFormat = DocumentFormat.DEFAULT
    ):
        if format == DocumentFormat.DEFAULT:
            return f"{self._id}/{file_suffix}"
        else:
            file_suffix = f"{os.path.splitext(file_suffix)[0]}.{format.value}"
            return f"{self._id}/{file_suffix}"

    async def _load_directory(self):
        async for file in self.remote_store.list_files(self.id):
            if self._is_index_file(file):
                index_name = os.path.dirname(file)
                base = os.path.basename(file)
                if index_name not in self.index_files:
                    self.index_files[index_name] = [base]
                else:
                    self.index_files[index_name].append(base)
            else:
                parts = os.path.splitext(file)
                base = parts[0]
                ext = parts[1]

                if base not in self.data_files:
                    self.data_files[base] = DataFileInfo(
                        default_file_name=file, extensions=[ext]
                    )
                else:
                    dfi = self.data_files[base]
                    if dfi.default_file_name.endswith(".txt"):
                        dfi.default_file_name = file
                    else:
                        dfi.extensions.append(ext)

            self.dir = [
                file_info.default_file_name for file_info in self.data_files.values()
            ]

    async def _add_data_file(self, file: DocumentSourceFile):
        content = file.read_content()
        print("UUID:", self.id)
        target_file_name = self._filename(file.filename())
        print("Target File Name:", target_file_name)
        await self.local_store.write_file(target_file_name, content)
        await self.remote_store.write_file(target_file_name, content)

    async def _init_from_zip(self, zip_src_file: DocumentSourceFile):
        zip_contents = await zip_src_file.read_content()
        with ZipFile(BytesIO(zip_contents), "r") as zf:
            async with asyncio.TaskGroup() as task_group:
                for file_info in zf.infolist():
                    filename = file_info.filename
                    if filename.startswith("__MACOSX/") or filename.endswith(
                            ".DS_Store"):
                        continue

                    zip_source_file = DocumentSourceFile(
                        filename, ZipFileReader(zf, file_info)
                    )

                    task_group.create_task(self._add_data_file(zip_source_file))

    async def init_from_files(self, files: List[DocumentSourceFile]):
        async with asyncio.TaskGroup() as task_group:
            for file in files:
                if file.filename().endswith(".zip"):
                    task_group.create_task(self._init_from_zip(file))
                else:
                    print("INSIDE ELSE")
                    task_group.create_task(self._add_data_file(file))

    async def list_files(self) -> AsyncIterator[str]:
        await self._load_directory()
        for file in self.dir:
            yield file

    async def read_file(
        self,
        filename: str,
        format: DocumentFormat = DocumentFormat.DEFAULT,
    ) -> bytes:
        full_filename = self._filename(filename, format)
        return await self.local_store.read_file(full_filename)

    async def write_file(
        self,
        filename: str,
        content: bytes,
        format: DocumentFormat = DocumentFormat.DEFAULT,
    ) -> bytes:
        return await self.local_store.write_file(
            self._filename(filename, format), content
        )

    async def write_audio_file(
        self,
        filename: str,
        content: bytes,
    ) -> bytes:
        return await self.remote_store.write_file(filename, content)

    def local_file_path(
        self, filename: str, format: DocumentFormat = DocumentFormat.DEFAULT
    ) -> str:
        target_file_name = self._filename(filename, format)
        return self.local_store.path(target_file_name)

    async def audio_file_public_url(self, filename: str) -> str:
        return await self.remote_store.make_public(filename)

    async def public_url(
        self, filename: str, format: DocumentFormat = DocumentFormat.DEFAULT
    ) -> str:
        target_file_name = self._filename(filename, format)
        return await self.remote_store.make_public(target_file_name)

    def _index_folder(self, indexer: str):
        return f"{self._id}/{indexer}"

    def _index_filename(self, indexer: str, file_suffix: str):
        return f"{self._index_folder(indexer)}/{file_suffix}"

    def _index_filename_fallback(self, indexer: str, file_suffix: str) -> str:
        return self._filename(file_suffix)

    async def download_index_files(self, indexer: str, *filenames: str) -> str:
        for filename in filenames:
            index_file_name = self._index_filename(indexer, filename)
            content = await self.read_index_file(indexer, filename)
            await self.local_store.write_file(index_file_name, content)
        return self._index_folder(indexer)

    async def read_index_file(self, indexer: str, filename: str) -> bytes:
        index_file_name = self._index_filename(indexer, filename)
        index_file_name_fallback = self._index_filename_fallback(indexer, filename)
        if not await self.local_store.file_exists(index_file_name):
            if await self.remote_store.file_exists(index_file_name):
                content = await self.remote_store.read_file(index_file_name)
            elif await self.remote_store.file_exists(index_file_name_fallback):
                content = await self.remote_store.read_file(index_file_name_fallback)
            else:
                raise FileNotFoundError(f"file {filename} not found")
        else:
            content = await self.local_store.read_file(index_file_name)

        return content

    async def write_index_file(
        self, indexer: str, filename: str, content: bytes
    ) -> bytes:
        return await self.remote_store.write_file(
            self._index_filename(indexer, filename), content
        )

    def local_index_folder(self, indexer: str) -> str:
        return os.path.join(
            os.environ["DOCUMENT_LOCAL_STORAGE_PATH"], self._index_folder(indexer)
        )

    def local_index_file_path(self, indexer: str, filename: str) -> str:
        target_file_name = self._index_filename(indexer, filename)
        return self.local_store.path(target_file_name)


class DocumentRepository:
    def __init__(
        self,
        local_store: Storage,
        remote_store: Storage,
    ):
        self.local_store = local_store
        self.remote_store = remote_store

    def new_collection(self) -> DocumentCollection:
        uuid_number = str(uuid.uuid1())
        new_collection = DocumentCollection(
            uuid_number, self.local_store, self.remote_store
        )
        return new_collection

    def get_collection(self, doc_id: str) -> DocumentCollection:
        return DocumentCollection(doc_id, self.local_store, self.remote_store)

    async def shutdown(self):
        await self.remote_store.shutdown()
        await self.local_store.shutdown()
