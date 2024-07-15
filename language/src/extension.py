"""This module is used to configure the language extension."""

from lib.speech_processor import (
    AzureSpeechProcessor,
    CompositeSpeechProcessor,
    DhruvaSpeechProcessor,
)
from lib.translator import AzureTranslator, CompositeTranslator, DhruvaTranslator
from lib.file_storage import StorageHandler

# ---- Speech Processor ----
speech_processor = CompositeSpeechProcessor(
    DhruvaSpeechProcessor(), AzureSpeechProcessor()
)

# ---- Translator ----
translator = CompositeTranslator(DhruvaTranslator(), AzureTranslator())

# ---- Storage ----
storage = StorageHandler.get_async_instance()
