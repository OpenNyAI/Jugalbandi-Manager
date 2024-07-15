text_message = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "test_id_1",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test_phone_number_1",
                            "phone_number_id": "test_phone_number_id_1",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "John Doe"},
                                "wa_id": "test_wa_id_1",
                            }
                        ],
                        "messages": [
                            {
                                "from": "test_wa_id_1",
                                "id": "test_message_id_1",
                                "timestamp": "test_timestamp_1",
                                "text": {"body": "How are you?"},
                                "type": "text",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

audio_message = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "test_id_2",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test_phone_number_2",
                            "phone_number_id": "test_phone_number_id_2",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "John Doe"},
                                "wa_id": "test_wa_id_2",
                            }
                        ],
                        "messages": [
                            {
                                "from": "test_wa_id_2",
                                "id": "test_message_id_2",
                                "timestamp": "test_timestamp_2",
                                "type": "audio",
                                "audio": {
                                    "mime_type": "audio/ogg; codecs=opus",
                                    "sha256": "test_sha256_1",
                                    "id": "test_audio_id_1",
                                    "voice": True,
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

button_reply = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "test_id_3",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test_phone_number_3",
                            "phone_number_id": "test_phone_number_id_3",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "John Doe"},
                                "wa_id": "test_wa_id_3",
                            }
                        ],
                        "messages": [
                            {
                                "context": {
                                    "from": "test_phone_number_3",
                                    "id": "test_context_id_1",
                                },
                                "from": "test_wa_id_3",
                                "id": "test_message_id_3",
                                "timestamp": "test_timestamp_3",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply",
                                    "button_reply": {"id": "0", "title": "Yes"},
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

list_reply = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "test_id_4",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test_phone_number_4",
                            "phone_number_id": "test_phone_number_id_4",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "John Doe"},
                                "wa_id": "test_wa_id_4",
                            }
                        ],
                        "messages": [
                            {
                                "context": {
                                    "from": "test_phone_number_4",
                                    "id": "test_context_id_2",
                                },
                                "from": "test_wa_id_4",
                                "id": "test_message_id_4",
                                "timestamp": "test_timestamp_4",
                                "type": "interactive",
                                "interactive": {
                                    "type": "list_reply",
                                    "list_reply": {
                                        "id": "lang_english",
                                        "title": "English",
                                    },
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

audio_hindi_message = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "test_id_5",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test_phone_number_5",
                            "phone_number_id": "test_phone_number_id_5",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "John Doe"},
                                "wa_id": "test_wa_id_5",
                            }
                        ],
                        "messages": [
                            {
                                "from": "test_wa_id_5",
                                "id": "test_message_id_5",
                                "timestamp": "test_timestamp_5",
                                "type": "audio",
                                "audio": {
                                    "mime_type": "audio/ogg; codecs=opus",
                                    "sha256": "test_sha256_2",
                                    "id": "test_audio_id_2",
                                    "voice": True,
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

text_hindi_message = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "test_id_6",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test_phone_number_6",
                            "phone_number_id": "test_phone_number_id_6",
                        },
                        "contacts": [
                            {
                                "profile": {"name": "John Doe"},
                                "wa_id": "test_wa_id_6",
                            }
                        ],
                        "messages": [
                            {
                                "from": "test_wa_id_6",
                                "id": "test_message_id_6",
                                "timestamp": "test_timestamp_6",
                                "text": {"body": "आप कैसे हैं"},
                                "type": "text",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}
