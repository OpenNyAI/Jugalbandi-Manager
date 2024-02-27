from logging_repository import LoggingRepository
from dotenv import load_dotenv
import asyncio


async def logging_db_population(logging_repository: LoggingRepository):
    await logging_repository.insert_users_information("Hello", "Bye", 91234567890)
    await logging_repository.insert_app_information("App1", 62846563489)
    await logging_repository.insert_users_information("John", "Doe", 1234567890)
    await logging_repository.insert_app_information("App2", 6371719192)
    await logging_repository.insert_document_store_log(1, 1, "545634353434", ["Hello", "Bye"],
                                                       40, 200, "Successful upload")
    await logging_repository.insert_qa_log("agsjasb1", 1, 1, "545634353434", "en", "How are you",
                                           "some-link", "I'm fine", "some-link", 5,
                                           ["1", "2", "3", "4"], "some-prompt", "gpt-4", 200,
                                           "Success", 10)
    await logging_repository.insert_qa_log("absahsg1", 2, 2, "545634353434", "es", "What's your name",
                                           "another-link", "My name is John", "another-link", 4,
                                           ["A", "B", "C", "D"], "another-prompt", "gpt-5", 201,
                                           "Success", 8)
    await logging_repository.insert_stt_log("agsjasb1", "some-link", "bhashini", "somshsdjf", 200,
                                            "success", 5)
    await logging_repository.insert_stt_log("absahsg1", "another-link", "google", "someother_audio_file", 404,
                                            "not_found", 10)
    await logging_repository.insert_tts_log("agsjasb1", "some-text", "bhashini", "some-link", 200,
                                            "success", 5)
    await logging_repository.insert_tts_log("absahsg1", "some-other-text", "google", "another-link", 500,
                                            "server_error", 7)
    await logging_repository.insert_translator_log("agsjasb1", "some-text", "hi", "en", "bhashini",
                                                   "translated-text", 200, "success", 5)
    await logging_repository.insert_translator_log("absahsg1", "some-other-text", "es", "fr", "john_doe",
                                                   "translated-text-2", 201, "Success", 6)
    await logging_repository.insert_chat_history(1, 1, "545634353434", "user", "en", "some-link",
                                                 "hello", "bye")
    await logging_repository.insert_chat_history(2, 2, "545634353434", "bot", "es", "another-link",
                                                 "Hola", "Adiós")


load_dotenv()
asyncio.run(logging_db_population(LoggingRepository()))
