import logging
import base64
from builtins import ExceptionGroup
import json
import os
import tempfile
from abc import ABC, abstractmethod

import azure.cognitiveservices.speech as speechsdk
import httpx
import boto3
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import requests
from botocore.exceptions import BotoCoreError, ClientError
import asyncio

from lib.model import InternalServerException, LanguageCodes
from .audio_converter import convert_wav_bytes_to_mp3_bytes

logger = logging.getLogger("speech_processor")


class SpeechProcessor(ABC):
    @abstractmethod
    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: LanguageCodes,
    ) -> str:
        pass

    @abstractmethod
    async def text_to_speech(
        self,
        text: str,
        input_language: LanguageCodes,
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
        input_language: LanguageCodes,
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
        input_language: LanguageCodes,
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
        input_language: LanguageCodes,
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
        input_language: LanguageCodes,
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


class AWSSpeechProcessor(SpeechProcessor):
    def __init__(self):
        # Set AWS credentials using environment variables
        os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
        os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
        os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION')

        self.transcribe = boto3.client('transcribe')
        self.s3 = boto3.client('s3') 
        self.polly = boto3.client('polly')
        self.bucket_name = os.get_env('S3_BUCKET_NAME')    

        self.language_dict = {
            "EN": "en-US",
            "HI": "hi-IN",
            "BN": "bn-IN",
            "GU": "gu-IN",
            "MR": "mr-IN",
            "KN": "kn-IN",
            "LU": "lg-IN",
            "EN-IN": "en-IN",
            "MA": "ml-IN",
            "OD": "or-IN",
            "PA": "pa-IN",
            "TA": "ta-IN",
            "TE": "te-IN",
        }

    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: LanguageCodes,
    ) -> str:
        logger.info("Performing speech to text using AWS Transcribe")
        logger.info(f"Input Language: {input_language.name}")

        try:
            # Upload the audio data to S3
            file_name = f"temp_audio_{input_language.name}.wav"
            self.s3.put_object(Bucket=self.bucket_name, Key=file_name, Body=wav_data)

            # Generate the S3 URI
            job_uri = f's3://{self.bucket_name}/{file_name}'

            # Start transcription job
            job_name = f"transcription_job_{input_language.name}"
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': job_uri},
                MediaFormat='wav',
                LanguageCode=self.language_dict.get(input_language.name, 'en-US')
            )

            # Wait for the job to complete
            while True:
                status = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
                if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                    break
                await asyncio.sleep(5)  # Wait for 5 seconds before checking again

            if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                file_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                response = requests.get(file_url)
                data = response.json()
                transcript = data['results']['transcripts'][0]['transcript']

                # Clean up: delete the temporary audio file from S3
                self.s3.delete_object(Bucket=self.bucket_name, Key=file_name)

                return transcript
            else:
                raise Exception("Transcription job failed")

        except (BotoCoreError, ClientError) as error:
            error_message = f"AWS STT Request failed with this error: {error}"
            logger.error(error_message)
            raise InternalServerException(error_message)

    async def text_to_speech(
        self,
        text: str,
        input_language: LanguageCodes,
    ) -> bytes:
        logger.info("Performing text to speech using AWS Polly")
        logger.info(f"Input Language: {input_language.name}")
        logger.info(f"Input Text: {text}")

        try:
            response = self.polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId='Joanna',  # You might want to choose appropriate voices for different languages
                LanguageCode=self.language_dict.get(input_language.name, 'en-US')
            )

            return response['AudioStream'].read()

        except (BotoCoreError, ClientError) as error:
            error_message = f"AWS TTS Request failed with this error: {error}"
            logger.error(error_message)
            raise InternalServerException(error_message)


class GCPSpeechProcessor(SpeechProcessor):
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.language_dict = {
            "EN": "en-US",
            "HI": "hi-IN",
            "BN": "bn-IN",
            "GU": "gu-IN",
            "MR": "mr-IN",
            "OR": "or-IN",
            "PA": "pa-Guru-IN",
            "KN": "kn-IN",
            "ML": "ml-IN",
            "TA": "ta-IN",
            "TE": "te-IN",
            "UR": "ur-IN",
            "EN-IN": "en-IN",
        }

    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: LanguageCodes,
    ) -> str:
        logger.info("Performing speech to text using Google Cloud Platform")
        logger.info(f"Input Language: {input_language.name}")

        audio = speech.RecognitionAudio(content=wav_data)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code=self.language_dict.get(input_language.name, "en-US"),
        )

        try:
            response = self.speech_client.recognize(config=config, audio=audio)
            transcribed_text = response.results[0].alternatives[0].transcript
            return_message = "GCP speech to text is successful"
            logger.info(return_message)
            logger.info(f"Transcribed text: {transcribed_text}")
            return transcribed_text
        except Exception as exception:
            error_message = f"GCP STT Request failed with this error: {exception}"
            logger.error(error_message)
            raise InternalServerException(error_message)

    async def text_to_speech(
        self,
        text: str,
        input_language: LanguageCodes,
    ) -> bytes:
        logger.info("Performing text to speech using Google Cloud Platform")
        logger.info(f"Input Language: {input_language.name}")
        logger.info(f"Input Text: {text}")

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.language_dict.get(input_language.name, "en-US"),
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            return_message = "GCP text to speech is successful"
            logger.info(return_message)
            return response.audio_content
        except Exception as exception:
            error_message = f"GCP TTS Request failed with this error: {exception}"
            logger.error(error_message)
            raise InternalServerException(error_message)


class CompositeSpeechProcessor(SpeechProcessor):
    def __init__(self, *speech_processors: SpeechProcessor):
        self.speech_processors = speech_processors
        self.european_language_codes = [
            "EN", "AF", "AR", "ZH", "FR", "DE", "ID", "IT", "JA", "KO", "PT", "RU", "ES", "TR"
        ]
        self.azure_not_supported_language_codes = ["OR", "PA"]
        self.gcp_not_supported_language_codes = []  # Add any unsupported languages for GCP
        self.aws_not_supported_language_codes = []  # Add any unsupported languages for AWS

    async def speech_to_text(
        self,
        wav_data: bytes,
        input_language: LanguageCodes,
    ) -> str:
        excs = []
        for speech_processor in self.speech_processors:
            if input_language.name in self.european_language_codes and isinstance(
                speech_processor, DhruvaSpeechProcessor
            ):
                continue
            elif (
                input_language.name in self.azure_not_supported_language_codes
                and isinstance(speech_processor, AzureSpeechProcessor)
            ):
                continue
            elif (
                input_language.name in self.gcp_not_supported_language_codes
                and isinstance(speech_processor, GCPSpeechProcessor)
            ):
                continue
            elif (
                input_language.name in self.aws_not_supported_language_codes
                and isinstance(speech_processor, AWSSpeechProcessor)
            ):
                continue
            else:
                try:
                    return await speech_processor.speech_to_text(wav_data, input_language)
                except Exception as exc:
                    excs.append(exc)

        raise ExceptionGroup("CompositeSpeechProcessor speech to text failed", excs)

    async def text_to_speech(
        self,
        text: str,
        input_language: LanguageCodes,
    ) -> bytes:
        excs = []
        for speech_processor in self.speech_processors:
            if input_language.name in self.european_language_codes and isinstance(
                speech_processor, DhruvaSpeechProcessor
            ):
                continue
            elif (
                input_language.name in self.azure_not_supported_language_codes
                and isinstance(speech_processor, AzureSpeechProcessor)
            ):
                continue
            elif (
                input_language.name in self.gcp_not_supported_language_codes
                and isinstance(speech_processor, GCPSpeechProcessor)
            ):
                continue
            elif (
                input_language.name in self.aws_not_supported_language_codes
                and isinstance(speech_processor, AWSSpeechProcessor)
            ):
                continue
            else:
                try:
                    return await speech_processor.text_to_speech(text, input_language)
                except Exception as exc:
                    excs.append(exc)

        raise ExceptionGroup("CompositeSpeechProcessor text to speech failed", excs)
    