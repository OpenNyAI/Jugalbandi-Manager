import logging
import base64
from builtins import ExceptionGroup
import json
import os
import tempfile
from abc import ABC, abstractmethod

import azure.cognitiveservices.speech as speechsdk
import httpx

from .model import InternalServerException, Language
from .audio_converter import convert_wav_bytes_to_mp3_bytes

logger = logging.getLogger("speech_processor")


class SpeechProcessor(ABC):
    @abstractmethod
    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: Language,
    ) -> str:
        pass

    @abstractmethod
    async def text_to_speech(
        self,
        text: str,
        input_language: Language,
    ) -> bytes:
        pass


class DhruvaSpeechProcessor(SpeechProcessor):
    def __init__(self):
        self.bhashini_user_id = os.getenv("BHASHINI_USER_ID")
        self.bhashini_api_key = os.getenv("BHASHINI_API_KEY")
        self.bhashini_pipleline_id = os.getenv("BHASHINI_PIPELINE_ID")
        self.bhashini_inference_url = (
            "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
        )

    async def perform_bhashini_config_call(
        self, task: str, source_language: str, target_language: str | None = None
    ):
        url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"
        if task in ["asr", "tts"]:
            payload = json.dumps(
                {
                    "pipelineTasks": [
                        {
                            "taskType": task,
                            "config": {"language": {"sourceLanguage": source_language}},
                        }
                    ],
                    "pipelineRequestConfig": {"pipelineId": "64392f96daac500b55c543cd"},
                }
            )
        else:
            payload = json.dumps(
                {
                    "pipelineTasks": [
                        {
                            "taskType": "translation",
                            "config": {
                                "language": {
                                    "sourceLanguage": source_language,
                                    "targetLanguage": target_language,
                                }
                            },
                        }
                    ],
                    "pipelineRequestConfig": {"pipelineId": self.bhashini_pipleline_id},
                }
            )
        headers = {
            "userID": self.bhashini_user_id,
            "ulcaApiKey": self.bhashini_api_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=payload)  # type: ignore

        return response.json()

    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: Language,
    ) -> str:
        logger.info("Performing speech to text using Dhruva (Bhashini)")
        logger.info(f"Input Language: {input_language.name}")
        bhashini_asr_config = await self.perform_bhashini_config_call(
            task="asr", source_language=input_language.name.lower()
        )
        encoded_string = base64.b64encode(wav_data).decode("ascii", "ignore")

        logger.info("Encoding wav data to string is successful")
        payload = json.dumps(
            {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "language": {
                                "sourceLanguage": bhashini_asr_config["languages"][0][
                                    "sourceLanguage"
                                ],
                            },
                            "serviceId": bhashini_asr_config["pipelineResponseConfig"][
                                0
                            ]["config"][0]["serviceId"],
                            "audioFormat": "wav",
                            "samplingRate": 16000,
                        },
                    }
                ],
                "inputData": {"audio": [{"audioContent": encoded_string}]},
            }
        )
        headers = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            bhashini_asr_config["pipelineInferenceAPIEndPoint"]["inferenceApiKey"][
                "name"
            ]: bhashini_asr_config["pipelineInferenceAPIEndPoint"]["inferenceApiKey"][
                "value"
            ],
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.bhashini_inference_url, headers=headers, data=payload
            )  # type: ignore
        if response.status_code != 200:
            error_message = (
                f"Request failed with response.text: {response.text} and "
                f"status_code: {response.status_code}"
            )
            logger.error(error_message)
            # await logging_repository.insert_stt_log(
            #     id=str(uuid.uuid1()),
            #     qa_log_id=qa_id,
            #     audio_input_bytes=str(wav_data),
            #     model_name="Bhashini",
            #     text="",
            #     status_code=response.status_code,
            #     status_message=response.text,
            #     response_time=10,
            # )
            raise InternalServerException(error_message)

        transcribed_text = response.json()["pipelineResponse"][0]["output"][0]["source"]
        return_message = "Dhruva (Bhashini) speech to text is successful"
        logger.info(return_message)
        logger.info(f"Transcribed text: {transcribed_text}")
        # await logging_repository.insert_stt_log(
        #     id=str(uuid.uuid1()),
        #     qa_log_id=qa_id,
        #     audio_input_bytes=str(wav_data),
        #     model_name="Bhashini",
        #     text=transcribed_text,
        #     status_code=200,
        #     status_message=return_message,
        #     response_time=10,
        # )
        return transcribed_text

    async def text_to_speech(
        self,
        text: str,
        input_language: Language,
        gender="female",
    ) -> bytes:
        logger.info("Performing text to speech using Dhruva (Bhashini)")
        logger.info(f"Input Language: {input_language.name}")
        logger.info(f"Input Text: {text}")
        bhashini_tts_config = await self.perform_bhashini_config_call(
            task="tts", source_language=input_language.name.lower()
        )

        payload = json.dumps(
            {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": bhashini_tts_config["languages"][0][
                                    "sourceLanguage"
                                ]
                            },
                            "serviceId": bhashini_tts_config["pipelineResponseConfig"][
                                0
                            ]["config"][0]["serviceId"],
                            "gender": gender,
                            "samplingRate": 8000,
                        },
                    }
                ],
                "inputData": {"input": [{"source": text}]},
            }
        )
        headers = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            # Why is it there?
            bhashini_tts_config["pipelineInferenceAPIEndPoint"]["inferenceApiKey"][
                "name"
            ]: bhashini_tts_config["pipelineInferenceAPIEndPoint"]["inferenceApiKey"][
                "value"
            ],
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.bhashini_inference_url, headers=headers, data=payload
            )  # type: ignore
        if response.status_code != 200:
            error_message = (
                f"Request failed with response.text: {response.text} and "
                f"status_code: {response.status_code}"
            )
            logger.error(error_message)
            # await logging_repository.insert_tts_log(
            #     id=str(uuid.uuid1()),
            #     qa_log_id=qa_id,
            #     text=text,
            #     model_name="Bhashini",
            #     audio_output_bytes="",
            #     status_code=response.status_code,
            #     status_message=response.text,
            #     response_time=10,
            # )
            raise InternalServerException(error_message)

        audio_content = response.json()["pipelineResponse"][0]["audio"][0][
            "audioContent"
        ]
        audio_content = base64.b64decode(audio_content)
        new_audio_content = convert_wav_bytes_to_mp3_bytes(audio_content)
        return_message = "Dhruva (Bhashini) text to speech is successful"
        logger.info(return_message)
        # await logging_repository.insert_tts_log(
        #     id=str(uuid.uuid1()),
        #     qa_log_id=qa_id,
        #     text=text,
        #     model_name="Bhashini",
        #     audio_output_bytes=new_audio_content,
        #     status_code=200,
        #     status_message=return_message,
        #     response_time=10,
        # )
        return new_audio_content


class AzureSpeechProcessor(SpeechProcessor):
    def __init__(self):
        self.language_dict = {
            "EN": ["en-IN", "en-IN-NeerjaNeural"],
            "HI": ["hi-IN", "hi-IN-SwaraNeural"],
            "BN": ["bn-IN", "bn-IN-TanishaaNeural"],
            "GU": ["gu-IN", "gu-IN-DhwaniNeural"],
            "MR": ["mr-IN", "mr-IN-AarohiNeural"],
            # "OR" : ["or-IN"], STT & TTS Not supported
            # "PA" : ["pa-IN"],  # TTS not supported
            "KN": ["kn-IN", "kn-IN-SapnaNeural"],
            "ML": ["ml-IN", "ml-IN-SobhanaNeural"],
            "TA": ["ta-IN", "ta-IN-PallaviNeural"],
            "TE": ["te-IN", "te-IN-ShrutiNeural"],
            "AF": ["af-ZA", "af-ZA-AdriNeural"],
            "AR": ["ar-DZ", "ar-DZ-AminaNeural"],
            "ZH": ["yue-CN", "yue-CN-XiaoMinNeural"],  # Chinese (Cantonese, Simplified)
            "FR": ["fr-FR", "fr-FR-DeniseNeural"],
            "DE": ["de-DE", "de-DE-KatjaNeural"],
            "ID": ["id-ID", "id-ID-GadisNeural"],
            "IT": ["it-IT", "it-IT-ElsaNeural"],
            "JA": ["ja-JP", "ja-JP-NanamiNeural"],
            "KO": ["ko-KR", "ko-KR-SunHiNeural"],
            "PT": ["pt-PT", "pt-PT-RaquelNeural"],
            "RU": ["ru-RU", "ru-RU-SvetlanaNeural"],
            "ES": ["es-ES", "es-ES-ElviraNeural"],
            "TR": ["tr-TR", "tr-TR-EmelNeural"],
        }
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION"),
        )

    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: Language,
    ) -> str:
        logger.info("Performing speech to text using Azure")
        logger.info(f"Input Language: {input_language.name}")
        language_code = self.language_dict[input_language.name][0]
        temp_wav_file = tempfile.NamedTemporaryFile()
        temp_wav_file.write(wav_data)
        audio_config = speechsdk.AudioConfig(filename=temp_wav_file.name)
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
            language=language_code,
        )
        try:
            result = speech_recognizer.recognize_once_async().get()
        except Exception as exception:
            error_message = f"Request failed with this error: {exception}"
            logger.error(error_message)
            # await logging_repository.insert_stt_log(
            #     id=str(uuid.uuid1()),
            #     qa_log_id=qa_id,
            #     audio_input_bytes=str(wav_data),
            #     model_name="Azure",
            #     text="",
            #     status_code=500,
            #     status_message=error_message,
            #     response_time=10,
            # )
        if temp_wav_file:
            temp_wav_file.close()

        transcribed_text = result.text
        return_message = "Azure speech to text is successful"
        logger.info(return_message)
        logger.info(f"Transcribed text: {transcribed_text}")
        # await logging_repository.insert_stt_log(
        #     id=str(uuid.uuid1()),
        #     qa_log_id=qa_id,
        #     audio_input_bytes=str(wav_data),
        #     model_name="Azure",
        #     text=transcribed_text,
        #     status_code=200,
        #     status_message=return_message,
        #     response_time=10,
        # )
        return transcribed_text

    async def text_to_speech(
        self,
        text: str,
        input_language: Language,
    ) -> bytes:
        logger.info("Performing text to speech using Azure")
        logger.info(f"Input Language: {input_language.name}")
        logger.info(f"Input Text: {text}")
        voice_language_code = self.language_dict[input_language.name][1]
        temp_output_file = tempfile.NamedTemporaryFile()
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_output_file.name)
        self.speech_config.speech_synthesis_voice_name = voice_language_code
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )
        try:
            speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        except Exception as exception:
            error_message = f"Request failed with this error: {exception}"
            logger.error(error_message)
            # await logging_repository.insert_tts_log(
            #     id=str(uuid.uuid1()),
            #     qa_log_id=qa_id,
            #     text=text,
            #     model_name="Azure",
            #     audio_output_bytes="",
            #     status_code=500,
            #     status_message=error_message,
            #     response_time=10,
            # )
        if temp_output_file:
            temp_output_file.close()

        audio_content = speech_synthesis_result.audio_data
        new_audio_content = convert_wav_bytes_to_mp3_bytes(audio_content)
        return_message = "Azure text to speech is successful"
        logger.info(return_message)
        # await logging_repository.insert_tts_log(
        #     id=str(uuid.uuid1()),
        #     qa_log_id=qa_id,
        #     text=text,
        #     model_name="Azure",
        #     audio_output_bytes=audio_content,
        #     status_code=200,
        #     status_message=return_message,
        #     response_time=10,
        # )
        return new_audio_content


class CompositeSpeechProcessor(SpeechProcessor):
    def __init__(self, *speech_processors: SpeechProcessor):
        self.speech_processors = speech_processors
        self.european_language_codes = [
            "EN",
            "AF",
            "AR",
            "ZH",
            "FR",
            "DE",
            "ID",
            "IT",
            "JA",
            "KO",
            "PT",
            "RU",
            "ES",
            "TR",
        ]
        self.azure_not_supported_language_codes = ["OR", "PA"]

    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: Language,
    ) -> str:
        excs = []
        for speech_processor in self.speech_processors:
            # try:
            if input_language.name in self.european_language_codes and isinstance(
                speech_processor, DhruvaSpeechProcessor
            ):
                pass
            elif (
                input_language.name in self.azure_not_supported_language_codes
                and isinstance(speech_processor, AzureSpeechProcessor)
            ):
                pass
            else:
                return await speech_processor.speech_to_text(wav_data, input_language)
            # except Exception as exc:
            #     print("EXCEPTION", exc)
            #     excs.append(exc)

        raise ExceptionGroup("CompositeSpeechProcessor speech to text failed", excs)

    async def text_to_speech(
        self,
        text: str,
        input_language: Language,
    ) -> bytes:
        excs = []
        for speech_processor in self.speech_processors:
            # try:
            if input_language.name in self.european_language_codes and isinstance(
                speech_processor, DhruvaSpeechProcessor
            ):
                pass
            elif (
                input_language.name in self.azure_not_supported_language_codes
                and isinstance(speech_processor, AzureSpeechProcessor)
            ):
                pass
            else:
                return await speech_processor.text_to_speech(text, input_language)
        #     except Exception as exc:
        #         excs.append(exc)

        # raise ExceptionGroup("CompositeSpeechProcessor text to speech failed", excs)
