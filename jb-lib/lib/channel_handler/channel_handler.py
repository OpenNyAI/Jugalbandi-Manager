from abc import ABC, abstractmethod
from typing import Dict, Generator, Optional
from pydantic import BaseModel
from lib.models import JBChannel, JBUser
from lib.data_models import (
    Message,
    BotInput,
    MessageType,
    TextMessage,
    InteractiveReplyMessage,
    FormReplyMessage,
    DialogMessage,
)


class User(BaseModel):
    """
    User object to store user related data.

    user_identifier: channel specific identifier for the user
    user_name: user name
    user_email: user email
    user_phone: user phone number
    """

    user_identifier: str
    user_name: str
    user_email: Optional[str] = None
    user_phone: Optional[str] = None


class ChannelData(BaseModel):
    """
    ChannelData object to store the user and message_data.
    """

    user: User
    message_data: Dict


class ChannelHandler(ABC):

    @classmethod
    @abstractmethod
    def is_valid_data(cls, data: Dict) -> bool:
        """
        Check if the given payload is valid for the given channel.
        This method is called in api layer of JBManager.
        """

    @classmethod
    @abstractmethod
    def get_channel_name(cls) -> str:
        """
        Return the name of the channel
        """

    @classmethod
    @abstractmethod
    def process_message(cls, data: Dict) -> Generator[ChannelData, None, None]:
        """
        This method should process the recieved payload and yield the ChannelData object.
        The ChannelData object should contain the user and message_data.
        message_data is an intermediate output with no PII data.
        message_data is parsed in channel layer by specific methods such as
        to_text_message, to_interactive_reply_message, to_form_reply_message, to_dialog_message.

        This method is called in api layer of JBManager.

        Args:
            data (Dict): Dictionary containing the payload recieved from the channel
        """

    @classmethod
    @abstractmethod
    def get_message_type(cls, bot_input: BotInput) -> MessageType:
        """
        Returns the type of the recieved message
        This method is called in channel layer of JBManager.

        BotInput is an abstract class, the actual implementation of the BotInput should be used.
        For example, RestBotInput should be used to determine the message type for REST channels.
        In the definition, type of bot_input will override by the exact subclass of BotInput.

        Args:
            bot_input (BotInput): BotInput object
        """

    @classmethod
    @abstractmethod
    def to_text_message(cls, bot_input: BotInput) -> TextMessage:
        """
        Convert the given bot_input to a TextMessage object, assuming the message type is text.
        This method is called in channel layer of JBManager.

        BotInput is an abstract class, the actual implementation of the BotInput should be used.
        For example, RestBotInput should be used to determine the message type for REST channels.
        In the definition, type of bot_input will override by the exact subclass of BotInput.

        Args:
            bot_input (BotInput): BotInput object
        """

    @classmethod
    @abstractmethod
    def get_audio(cls, channel: JBChannel, bot_input: BotInput) -> bytes:
        """
        Get the base64 encoded audio from the given bot input and channel.
        channel is used to determine the channel specific credentials for audio extraction.
        This method is called in channel layer of JBManager.

        BotInput is an abstract class, the actual implementation of the BotInput should be used.
        For example, RestBotInput should be used to determine the message type for REST channels.
        In the definition, type of bot_input will override by the exact subclass of BotInput.

        Args:
            bot_input (BotInput): BotInput object
        """

    @classmethod
    @abstractmethod
    def to_interactive_reply_message(
        cls, bot_input: BotInput
    ) -> InteractiveReplyMessage:
        """
        Convert the bot_input to an InteractiveReplyMessage object, assuming interactive reply.
        This method is called in channel layer of JBManager.

        BotInput is an abstract class, the actual implementation of the BotInput should be used.
        For example, RestBotInput should be used to determine the message type for REST channels.
        In the definition, type of bot_input will override by the exact subclass of BotInput.

        Args:
            bot_input (BotInput): BotInput object
        """

    @classmethod
    @abstractmethod
    def to_form_reply_message(cls, bot_input: BotInput) -> FormReplyMessage:
        """
        Convert the given bot_input to a FormReplyMessage object, assuming the message type is form.
        This method is called in channel layer of JBManager.

        BotInput is an abstract class, the actual implementation of the BotInput should be used.
        For example, RestBotInput should be used to determine the message type for REST channels.
        In the definition, type of bot_input will override by the exact subclass of BotInput.

        Args:
            bot_input (BotInput): BotInput object
        """

    @classmethod
    @abstractmethod
    def to_dialog_message(cls, bot_input: BotInput) -> DialogMessage:
        """
        Convert the given bot_input to a DialogMessage object, assuming the message type is dialog.
        Currently JBManager supports language selected as the dialog type for message from user.
        This method is called in channel layer of JBManager.


        BotInput is an abstract class, the actual implementation of the BotInput should be used.
        For example, RestBotInput should be used to determine the message type for REST channels.
        In the definition, type of bot_input will override by the exact subclass of BotInput.

        Args:
            bot_input (BotInput): BotInput object
        """

    @classmethod
    @abstractmethod
    def parse_bot_output(
        cls, message: Message, user: JBUser, channel: JBChannel
    ) -> Dict:
        """
        Convert the given message to a dictionary that can be sent as a payload to sent to the user.
        channel shall be used to determine the channel specific credentials for sending the message.
        user is used to determine the user specific data for sending the message.

        Args:
            message (Message): Message object
            user (JBUser): JBUser object
            channel (JBChannel): JBChannel object
        """

    @classmethod
    @abstractmethod
    def send_message(cls, channel: JBChannel, user: JBUser, message: Message):
        """
        Send the given message to the user using the given channel.
        This method shall use the parse_bot_output method.
        The dictionary shall be sent to the channel to be sent to the user.

        This method is called in channel layer of JBManager.


        Args:
            channel (JBChannel): JBChannel object
            user (JBUser): JBUser object
            message (Message): Message object
        """
