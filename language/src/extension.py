"""This module is used to configure the language extension."""
import os
from lib.azure_storage import AzureStorage
from lib.speech_processor import (
    AzureSpeechProcessor,
    CompositeSpeechProcessor,
    DhruvaSpeechProcessor,
)
from lib.translator import AzureTranslator, CompositeTranslator, DhruvaTranslator

# ---- Speech Processor ----
speech_processor = CompositeSpeechProcessor(
    DhruvaSpeechProcessor(), AzureSpeechProcessor()
)

# ---- Translator ----
translator = CompositeTranslator(DhruvaTranslator(), AzureTranslator())

# ---- Storage ----
account_url = os.getenv("STORAGE_ACCOUNT_URL")
account_key = os.getenv("STORAGE_ACCOUNT_KEY")
container_name = os.getenv("STORAGE_AUDIOFILES_CONTAINER")
storage = AzureStorage(
    account_url=account_url,
    account_key=account_key,
    container_name=container_name,
    base_path="output_files/",
)
