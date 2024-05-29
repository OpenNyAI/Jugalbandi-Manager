---
layout: default
title: FSMOutput
---

The purpose of `FSMOutput` is to give a structured and defined data structure to communicate between Bot code and JBManager framework. Instance of `FSMOutput` is passed as an arguement while calling the `send_message` function.

```python
class FSMOutput:
    dest: str = "out"
    type: MessageType = MessageType.TEXT
    message_data: MessageData
    options_list: Optional[List[OptionsListType]] = None
    media_url: Optional[str] = None
    file: Optional[UploadFile] = None
    whatsapp_flow_id: Optional[str] = None
    whatsapp_screen_id: Optional[str] = None
    menu_selector: Optional[str] = None
    menu_title: Optional[str] = None
    form_token: Optional[str] = None
    plugin_uuid: Optional[str] = None
    dialog: Optional[str] = None
```

1. `dest` - This represents the corresponding layer in JBManager to which the message needs to be sent. Possible destinations:
    * `out` - The message will follow translation(if applicable) and converted to speech and sent it to user.
    * `channel` - There are some messages which don't require translation and should be interpreted as a special message. Those could be either flags for language selection or metadata for the forms which will be displayed to user.
    * `rag` - The message will go to RAG component of JBManager instead of user.  
2. `type` - Represents the type of the message which needs to be send to user. It will be of enum of type `MessageType`. See `MessageType` for info regarding the supported message types.
3. `message_data` - Body of the message which will be sent to the user.
4. `options_list` - List of options which will be presented to user. Only used in case of interactive message.
5. `media_url` - Url of the file(image/audio/document) which needs to be send to the user along with message body. Only used in case of image, document and audio message.
6. `file` - Document to send to the user along with message body. Only used in case of document message.
7. `whatsapp_flow_id` - Flow ID required to identify the form to send to user in whatsapp. Only used in case of form message.
8. `whatsapp_screen_id` - Screen ID required to identify the form screen to send to user in whatsapp. Only used in case of form message.
9. `menu_selector` - In case options are displayed in form of list to the user(number of options > 3), this represents the text on the button which opens the list of options. Only used in case of interactive message.
10. `menu_title` - In case options are displayed in form of list to the user(number of options > 3), this represents the text on the panel showing list of options. Only used in case of interactive message.
11. `form_token` - Token to identify the form to send to user.
12. `plugin_uuid` - This represents the uniqueID used to require to identify the current running session in case of an 3rd party webhook input. Here, the expectation is that this unique ID is used to call the 3rd party plugin and this will be returned in the webhook call.
13. `dialog` - It represents various signals sent to JBManager framework which will trigger certain existing flows which are a part of JBManager. Currently supported options:
    * `language` - Represents the signal to send the language selector option to the user on which user will select the preferred language.


```python
class MessageData:
    header: Optional[str] = None
    body: str
    footer: Optional[str] = None
```
1. `header` - Header of the message body. Only used incase of interactive and form message.
2. `body` - Message text which needs to be displayed.
3. `footer` - Footer of the message body. Only used incase of interactive and form message.

```python
class OptionsListType:
    id: str
    title: str
```
1. `id` - Option Identifier. This value of the selected option will be returned to the bot code.
2. `title` - This value will be displayed to the user as text on the option.

### Supported Message Type

The following message types are supported as defined by the enum `MessageType`
```python
class MessageType(Enum):
    """
    Enum class to define the type of message.
    """
    INTERACTIVE = "interactive"
    TEXT = "text"
    AUDIO = "audio"
    DOCUMENT = "document"
    FORM = "form"
    IMAGE = "image"
    DIALOG = "dialog"
```
