import operator
import os
from datetime import datetime
from typing import Annotated, Dict, Optional

import asyncpg
import pytz
from dotenv import load_dotenv

from .aio_caching import aiocachedmethod

load_dotenv()


class LoggingRepository:
    def __init__(self) -> None:
        self.engine_cache: Dict[str, asyncpg.Pool] = {}

    @aiocachedmethod(operator.attrgetter("engine_cache"))
    async def _get_engine(self) -> asyncpg.Pool:
        engine = await self._create_engine()
        return engine

    async def _create_engine(self, timeout=5):
        engine = await asyncpg.create_pool(
            host=os.getenv("POSTGRES_DATABASE_HOST"),
            port=os.getenv("POSTGRES_DATABASE_PORT"),
            user=os.getenv("POSTGRES_DATABASE_USERNAME"),
            password=os.getenv("POSTGRES_DATABASE_PASSWORD"),
            database=os.getenv("POSTGRES_DATABASE_NAME"),
            max_inactive_connection_lifetime=timeout,
        )
        return engine

    async def insert_users_information(self, pid: str, first_name: str,
                                       last_name: str,
                                       phone_number: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_users
                (pid, first_name, last_name, phone_number, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                pid,
                first_name,
                last_name,
                phone_number,
                datetime.now(pytz.UTC),
            )

    async def insert_bot_information(self, bot_id: str, name: str,
                                     phone_number: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_bot
                (bot_id, name, phone_number, created_at)
                VALUES ($1, $2, $3, $4)
                """,
                bot_id,
                name,
                phone_number,
                datetime.now(pytz.UTC),
            )

    async def insert_document_store_log(self, bot_id: str, uuid: str,
                                        documents_list: list, total_file_size: int,
                                        status_code: int, status_message: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_document_store_log
                (bot_id, uuid, documents_list,
                total_file_size, status_code, status_message, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                bot_id,
                uuid,
                documents_list,
                total_file_size,
                status_code,
                status_message,
                datetime.now(pytz.UTC),
            )

    async def insert_qa_log(self, id: str, pid: str, bot_id: str, document_uuid: str, input_language: str,
                            query: str, audio_input_link: str, response: str, audio_output_link: str,
                            retrieval_k_value: int, retrieved_chunks: list, prompt: str, gpt_model_name: str,
                            status_code: int, status_message: str, response_time: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_qa_log
                (id, pid, bot_id, document_uuid, input_language,
                query, audio_input_link, response, audio_output_link,
                retrieval_k_value, retrieved_chunks, prompt, gpt_model_name,
                status_code, status_message, response_time, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11,
                $12, $13, $14, $15, $16, $17)
                """,
                id,
                pid,
                bot_id,
                document_uuid,
                input_language,
                query,
                audio_input_link,
                response,
                audio_output_link,
                retrieval_k_value,
                retrieved_chunks,
                prompt,
                gpt_model_name,
                status_code,
                status_message,
                response_time,
                datetime.now(pytz.UTC),
            )

    async def insert_stt_log(self, id: str, qa_log_id: str, audio_input_bytes: str,
                             model_name: str, text: str, status_code: int,
                             status_message: str, response_time: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_stt_log
                (id, qa_log_id, audio_input_bytes, model_name,
                text, status_code, status_message,
                response_time, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                id,
                qa_log_id,
                audio_input_bytes,
                model_name,
                text,
                status_code,
                status_message,
                response_time,
                datetime.now(pytz.UTC),
            )

    async def insert_tts_log(self, id: str, qa_log_id: str, text: str,
                             model_name: str, audio_output_bytes: str, status_code: int,
                             status_message: str, response_time: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_tts_log
                (id, qa_log_id, text, model_name,
                audio_output_bytes, status_code, status_message,
                response_time, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                id,
                qa_log_id,
                text,
                model_name,
                audio_output_bytes,
                status_code,
                status_message,
                response_time,
                datetime.now(pytz.UTC),
            )

    async def insert_translator_log(self, id: str, qa_log_id: str, text: str, input_language: str,
                                    output_language: str, model_name: str, translated_text: str,
                                    status_code: int, status_message: str, response_time: int):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_translator_log
                (id, qa_log_id, text, input_language, output_language,
                model_name, translated_text, status_code,
                status_message, response_time, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                id,
                qa_log_id,
                text,
                input_language,
                output_language,
                model_name,
                translated_text,
                status_code,
                status_message,
                response_time,
                datetime.now(pytz.UTC),
            )

    async def insert_chat_history(self, id: str, pid: str, bot_id: str, document_uuid: str,
                                  message_owner: str, preferred_language: str, audio_url: str,
                                  message: str, message_in_english: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO jb_chat_history
                (id, pid, bot_id, document_uuid,
                message_owner, preferred_language, audio_url,
                message, message_in_english, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                id,
                pid,
                bot_id,
                document_uuid,
                message_owner,
                preferred_language,
                audio_url,
                message,
                message_in_english,
                datetime.now(pytz.UTC),
            )

    async def get_user_preferred_language(self, pid: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                SELECT language_preference FROM jb_users
                WHERE pid = $1
                """,
                pid
            )

    async def get_user_pid(self, contact_number: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                SELECT pid FROM jb_users
                WHERE phone_number = $1
                """,
                contact_number
            )
        
    async def get_phone_number_from_user_table(self, pid: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchval(
                """
                SELECT phone_number FROM jb_users
                WHERE pid = $1
                """,
                pid
            )
        
    async def register_user_in_db(self, person_uid: str, first_name: str,
                                  last_name: str, contact_number: str,
                                  language_preference: str = 'en'):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO public.jb_users (pid, first_name, last_name, phone_number, language_preference)
                VALUES($1, $2, $3, $4, $5)
                """,
                person_uid, first_name, last_name, contact_number, language_preference
            )


    async def get_message_media_information(self, msg_id: str):
        engine = await self._get_engine()
        async with engine.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT media_type, media_url, user_text FROM jb_message
                WHERE msg_id = $1
                """,
                msg_id
            )
