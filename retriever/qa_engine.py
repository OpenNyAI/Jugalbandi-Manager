import time
from enum import Enum
from abc import ABC, abstractmethod
from pydantic import BaseModel
from lib.document_collection import DocumentCollection
from lib.speech_processor import SpeechProcessor
from lib.translator import Translator
from lib.audio_converter import convert_to_wav_with_ffmpeg
from lib.model import Language
from .model import MediaFormat
from .model import IncorrectInputException
from .query_with_langchain import querying_with_langchain
from lib.jb_logging import Logger
from lib.logging_repository import LoggingRepository
import uuid

logger = Logger("rag_engine")


class QueryResponse(BaseModel):
    query: str
    query_in_english: str = ""
    answer: str
    answer_in_english: str = ""
    audio_output_url: str = ""


class LangchainQAModel(Enum):
    GPT35_TURBO = "gpt-3.5-turbo-1106"
    GPT4 = "gpt-4"


class QAEngine(ABC):
    @abstractmethod
    async def query(
        self,
        query: str = "",
        speech_query_url: str = "",
        input_language: Language = Language.EN,
        output_format: MediaFormat = MediaFormat.TEXT,
    ) -> QueryResponse:
        pass


class LangchainQAEngine(QAEngine):
    def __init__(
        self,
        document_collection: DocumentCollection,
        speech_processor: SpeechProcessor,
        translator: Translator,
        model: LangchainQAModel,  # Remove (Customizable)
        logging_repository: LoggingRepository,
    ):
        self.document_collection = document_collection
        self.speech_processor = speech_processor
        self.translator = translator
        self.model = model
        self.logging_repository = logging_repository

    async def query(
        self,
        user_id: str,  # Should be customized (Backend)
        app_id: str,  # Should be customized (Backend)
        query: str = "",
        speech_query_url: str = "",
        prompt: str = "",  # May not be needed
        input_language: Language = Language.EN,
        output_format: MediaFormat = MediaFormat.TEXT,
    ) -> QueryResponse:
        qa_id = str(uuid.uuid1())
        logger.info(f"Querying with QA ID: {qa_id}")
        is_voice = False
        audio_output_url = ""
        if query == "" and speech_query_url == "":
            error_message = "Query input is missing"
            logger.error(error_message)
            await self.logging_repository.insert_qa_log(
                id=qa_id,
                user_id=user_id,
                app_id=app_id,
                document_uuid="some-predefined-id",
                input_language=input_language,
                query=query,
                audio_input_link=speech_query_url,
                response="",
                audio_output_link=audio_output_url,
                retrieval_k_value=0,
                retrieved_chunks=[],
                prompt="",
                gpt_model_name="",
                status_code=422,
                status_message=error_message,
                response_time=10,
            )
            raise IncorrectInputException(error_message)

        if query != "":
            logger.info("Query Type: Text")
            if output_format.name == "VOICE":
                logger.info("Response Type: Voice")
                is_voice = True
            else:
                logger.info("Response Type: Text")
        else:
            logger.info("Query Type: Voice")
            wav_data = await convert_to_wav_with_ffmpeg(speech_query_url)
            logger.info("Audio converted to wav")
            query = await self.speech_processor.speech_to_text(
                self.logging_repository, wav_data, input_language
            )
            logger.info("Response Type: Voice")
            is_voice = True

        logger.info(f"User Query: {query}")
        logger.info(
            "Query Input Language: " + input_language.value
        )
        query_in_english = await self.translator.translate_text(
            self.logging_repository, qa_id, query, input_language, Language.EN
        )
        k, chunks, prompt, answer_in_english = await querying_with_langchain(
            query_in_english, prompt, self.model.value
        )
        logger.info("RAG is successful")
        logger.info(f"Query in English: {query_in_english}")
        logger.info(f"K value: {str(k)}")
        logger.info(f"Chunks: {', '.join(chunks)}")
        logger.info(f"Prompt: {prompt}")
        logger.info(f"Answer in English: {answer_in_english}")

        answer = await self.translator.translate_text(
            self.logging_repository,
            qa_id,
            answer_in_english,
            Language.EN,
            input_language,
        )
        logger.info(f"Answer: {answer}")
        if is_voice:
            audio_content = await self.speech_processor.text_to_speech(
                self.logging_repository, qa_id, answer, input_language
            )
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "output_audio_files/audio-output-" + time_stamp + ".mp3"
            logger.info(f"Writing audio file: {filename}")
            await self.document_collection.write_audio_file(filename, audio_content)
            audio_output_url = await self.document_collection.audio_file_public_url(
                filename
            )
            logger.info(
                f"Audio output URL: {audio_output_url}"
            )

        return_message = "RAG Engine process completed successfully"
        logger.info(return_message)
        await self.logging_repository.insert_qa_log(
            id=qa_id,
            user_id=user_id,
            app_id=app_id,
            document_uuid="some-predefined-id",
            input_language=input_language,
            query=query,
            audio_input_link=speech_query_url,
            response=answer,
            audio_output_link=audio_output_url,
            retrieval_k_value=k,
            retrieved_chunks=chunks,
            prompt=prompt,
            gpt_model_name=self.model.value,
            status_code=200,
            status_message=return_message,
            response_time=10,
        )
        return QueryResponse(
            query=query,
            query_in_english=query_in_english,
            answer=answer,
            answer_in_english=answer_in_english,
            audio_output_url=audio_output_url,
        )
