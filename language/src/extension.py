"""This module is used to configure the language extension."""

from lib.file_storage import StorageHandler
from .speech_processor import (
    AzureSpeechProcessor,
    CompositeSpeechProcessor,
    DhruvaSpeechProcessor,
    AWSSpeechProcessor,
    GCPSpeechProcessor,
)
from .translator import AzureTranslator, CompositeTranslator, DhruvaTranslator, AWSTranslator, GCPTranslator

# ---- Speech Processor ----
speech_processor = CompositeSpeechProcessor(
    DhruvaSpeechProcessor(), AzureSpeechProcessor(), AWSSpeechProcessor(), GCPSpeechProcessor()
)

# ---- Translator ----
translator = CompositeTranslator(DhruvaTranslator(), AzureTranslator(), AWSTranslator(), GCPTranslator())

# ---- Storage ----
storage = StorageHandler.get_async_instance()
