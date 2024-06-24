import logging
import json
import os
import uuid
from abc import ABC, abstractmethod

import aiohttp
import httpx

from .model import InternalServerException, Language

logger = logging.getLogger("translator")


class Translator(ABC):
    @abstractmethod
    async def translate_text(
        self,
        text: str,
        source_language: Language,
        destination_language: Language,
    ) -> str:
        pass


class DhruvaTranslator(Translator):
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

    async def translate_text(
        self,
        text: str,
        source_language: Language,
        destination_language: Language,
    ) -> str:
        source = source_language.name.lower()
        destination = destination_language.name.lower()
        logger.info("Performing translation using Dhruva (Bhashini)")
        logger.info(f"Input Language: {source}")
        logger.info(f"Output Language: {destination}")

        bhashini_translation_config = await self.perform_bhashini_config_call(
            task="translation", source_language=source, target_language=destination
        )

        payload = json.dumps(
            {
                "pipelineTasks": [
                    {
                        "taskType": "translation",
                        "config": {
                            "language": {
                                "sourceLanguage": bhashini_translation_config[
                                    "languages"
                                ][0]["sourceLanguage"],
                                "targetLanguage": bhashini_translation_config[
                                    "languages"
                                ][0]["targetLanguageList"][0],
                            },
                            "serviceId": bhashini_translation_config[
                                "pipelineResponseConfig"
                            ][0]["config"][0]["serviceId"],
                        },
                    }
                ],
                "inputData": {"input": [{"source": text}]},
            }
        )
        headers = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            bhashini_translation_config["pipelineInferenceAPIEndPoint"][
                "inferenceApiKey"
            ]["name"]: bhashini_translation_config["pipelineInferenceAPIEndPoint"][
                "inferenceApiKey"
            ][
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
            # await logging_repository.insert_translator_log(
            #     id=str(uuid.uuid1()),
            #     qa_log_id=qa_id,
            #     text=text,
            #     input_language=source_language,
            #     output_language=destination_language,
            #     model_name="Bhashini",
            #     translated_text="",
            #     status_code=response.status_code,
            #     status_message=response.text,
            #     response_time=10,
            # )
            raise InternalServerException(error_message)

        indicText = response.json()["pipelineResponse"][0]["output"][0]["target"]
        return_message = "Dhruva (Bhashini) translation is successful"
        logger.info(return_message)
        logger.info(f"Input Text: {text}")
        logger.info(f"Translated Text: {indicText}")
        # await logging_repository.insert_translator_log(
        #     id=str(uuid.uuid1()),
        #     qa_log_id=qa_id,
        #     text=text,
        #     input_language=source_language,
        #     output_language=destination_language,
        #     model_name="Bhashini",
        #     translated_text=indicText,
        #     status_code=200,
        #     status_message=return_message,
        #     response_time=10,
        # )
        return indicText


class AzureTranslator(Translator):
    def __init__(self):
        self.subscription_key = os.getenv("AZURE_TRANSLATION_KEY")
        self.resource_location = os.getenv("AZURE_TRANSLATION_RESOURCE_LOCATION")
        self.endpoint = "https://api.cognitive.microsofttranslator.com"

    async def translate_text(
        self,
        text: str,
        source_language: Language,
        destination_language: Language,
    ) -> str:
        path = "/translate"
        constructed_url = self.endpoint + path

        if source_language.name == "ZH":
            source_language_code = "zh-Hans"
        else:
            source_language_code = source_language.name.lower()

        if destination_language.name == "ZH":
            destination_language_code = "zh-Hans"
        else:
            destination_language_code = destination_language.name.lower()

        logger.info("Performing translation using Azure")
        logger.info(f"Input Language: {source_language}")
        logger.info(f"Output Language: {destination_language}")
        params = {
            "api-version": "3.0",
            "from": source_language_code,
            "to": destination_language_code,
        }
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Ocp-Apim-Subscription-Region": self.resource_location,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        body = [{"text": text}]

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.post(
                constructed_url, params=params, headers=headers, json=body
            ) as response:
                try:
                    response = await response.json()
                except Exception as exception:
                    error_message = f"Request failed with this error: {exception}"
                    logger.error(error_message)
                    # await logging_repository.insert_translator_log(
                    #     id=str(uuid.uuid1()),
                    #     qa_log_id=qa_id,
                    #     text=text,
                    #     input_language=source_language,
                    #     output_language=destination_language,
                    #     model_name="Azure",
                    #     translated_text="",
                    #     status_code=500,
                    #     status_message=error_message,
                    #     response_time=10,
                    # )
                    raise InternalServerException(error_message)

                translated_text = response[0]["translations"][0]["text"]
                return_message = "Azure translation is successful"
                logger.info(return_message)
                logger.info(f"Input Text: {text}")
                logger.info(f"Translated Text: {translated_text}")
                # await logging_repository.insert_translator_log(
                #     id=str(uuid.uuid1()),
                #     qa_log_id=qa_id,
                #     text=text,
                #     input_language=source_language,
                #     output_language=destination_language,
                #     model_name="Azure",
                #     translated_text=translated_text,
                #     status_code=200,
                #     status_message=return_message,
                #     response_time=10,
                # )
                return translated_text

    async def transliterate_text(
        self, text: str, source_language: Language, from_script: str, to_script: str
    ) -> str:
        path = "/transliterate"
        constructed_url = self.endpoint + path

        params = {
            "api-version": "3.0",
            "language": source_language.name.lower(),
            "fromScript": from_script,
            "toScript": to_script,
        }
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Ocp-Apim-Subscription-Region": self.resource_location,
            "Content-type": "application/json",
            "X-ClientTraceId": str(uuid.uuid4()),
        }
        body = [{"text": text}]

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.post(
                constructed_url, params=params, headers=headers, json=body
            ) as response:
                response = await response.json()
                print(response)
                return response[0]["text"]


class CompositeTranslator(Translator):
    def __init__(self, *translators: Translator):
        self.translators = translators

    async def translate_text(
        self,
        text: str,
        source_language: Language,
        destination_language: Language,
    ) -> str:
        if source_language.value == destination_language.value:
            return text

        excs = []
        for translator in self.translators:
            try:
                return await translator.translate_text(
                    text,
                    source_language,
                    destination_language,
                )
            except Exception as exc:
                excs.append("Exception", exc)

        raise ExceptionGroup("CompositeTranslator translation failed", excs)
