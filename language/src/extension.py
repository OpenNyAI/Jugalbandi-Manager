"""This module is used to configure the language extension."""

from lib.file_storage import StorageHandler
from .speech_processor import (
    AzureSpeechProcessor,
    CompositeSpeechProcessor,
    DhruvaSpeechProcessor,
)
from .translator import AzureTranslator, CompositeTranslator, DhruvaTranslator

# ---- Speech Processor ----
speech_processor = CompositeSpeechProcessor(
    DhruvaSpeechProcessor(), AzureSpeechProcessor()
)

# ---- Translator ----
translator = CompositeTranslator(DhruvaTranslator(), AzureTranslator())

# ---- Storage ----
storage = StorageHandler.get_async_instance()
