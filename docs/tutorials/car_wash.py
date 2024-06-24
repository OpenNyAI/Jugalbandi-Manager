from datetime import datetime
import json
from os import error
import re
from typing import Any, Dict, Type

from jb_manager_bot import (
    AbstractFSM,
    FSMOutput,
    MessageData,
    MessageType,
    OptionsListType,
    Status,
)
from jb_manager_bot.parsers import OptionParser
from jb_manager_bot.parsers.utils import LLMManager


class CarWashDealerFSM(AbstractFSM):
    """
    This is the FSM class for the Car Wash Dealer project.
    """

    states = [
        "zero",
        "select_language",
        "welcome_message_display",
        "service_selection_display",
        "service_selection_input",
        "service_selection_logic",
        "service_selection_fail_display",
        "appointment_query_display",
        "date_input",
        "process_date_logic",
        "get_time_of_day_display",
        "time_of_day_input",
        "time_of_day_logic",
        "appointment_date_fail_display",
        "appointment_time_fail_display",
        "check_availability_plugin",
        "plugin_fail_display",
        "check_booking_status_logic",
        "booking_confirmation_display",
        "alternative_appointment_display",
        "further_assistance_display",
        "further_assistance_input",
        "process_further_assistance_logic",
        "further_assistance_fail_display",
        "conclusion_display",
        "end",
    ]
    transitions = [
        {"source": "zero", "dest": "select_language", "trigger": "next"},
        {
            "source": "select_language",
            "dest": "welcome_message_display",
            "trigger": "next",
        },
        {
            "source": "welcome_message_display",
            "dest": "service_selection_display",
            "trigger": "next",
        },
        {
            "source": "service_selection_display",
            "dest": "service_selection_input",
            "trigger": "next",
        },
        {
            "source": "service_selection_input",
            "dest": "service_selection_logic",
            "trigger": "next",
        },
        {
            "source": "service_selection_logic",
            "dest": "appointment_query_display",
            "trigger": "next",
            "conditions": "is_valid_service",
        },
        {
            "source": "service_selection_logic",
            "dest": "service_selection_fail_display",
            "trigger": "next",
        },
        {
            "source": "service_selection_fail_display",
            "dest": "service_selection_display",
            "trigger": "next",
        },
        {
            "source": "appointment_query_display",
            "dest": "date_input",
            "trigger": "next",
        },
        {
            "source": "date_input",
            "dest": "process_date_logic",
            "trigger": "next",
        },
        {
            "source": "process_date_logic",
            "dest": "get_time_of_day_display",
            "trigger": "next",
            "conditions": "is_valid_date",
        },
        {
            "source": "process_date_logic",
            "dest": "appointment_date_fail_display",
            "trigger": "next",
        },
        {
            "source": "appointment_query_display",
            "dest": "appointment_date_fail_display",
            "trigger": "next",
        },
        {
            "source": "appointment_date_fail_display",
            "dest": "appointment_query_display",
            "trigger": "next",
        },
        {
            "source": "get_time_of_day_display",
            "dest": "time_of_day_input",
            "trigger": "next",
        },
        {
            "source": "time_of_day_input",
            "dest": "time_of_day_logic",
            "trigger": "next",
        },
        {
            "source": "time_of_day_logic",
            "dest": "check_availability_plugin",
            "trigger": "next",
            "conditions": "is_valid_time",
        },
        {
            "source": "time_of_day_logic",
            "dest": "appointment_time_fail_display",
            "trigger": "next",
        },
        {
            "source": "appointment_time_fail_display",
            "dest": "get_time_of_day_display",
            "trigger": "next",
        },
        {
            "source": "check_availability_plugin",
            "dest": "check_booking_status_logic",
            "trigger": "next",
            "conditions": "is_error_code_200",
        },
        {
            "source": "check_availability_plugin",
            "dest": "plugin_fail_display",
            "trigger": "next",
            "conditions": "is_error_code_400",
        },
        {
            "source": "check_availability_plugin",
            "dest": "plugin_fail_display",
            "trigger": "next",
            "conditions": "is_error_code_500",
        },
        {
            "source": "check_availability_plugin",
            "dest": "plugin_fail_display",
            "trigger": "next",
            "conditions": "is_error_code_404",
        },
        {
            "source": "plugin_fail_display",
            "dest": "service_selection_display",
            "trigger": "next",
        },
        {
            "source": "check_booking_status_logic",
            "dest": "booking_confirmation_display",
            "trigger": "booking_confirmed",
            "conditions": "is_booking_confirmed",
        },
        {
            "source": "check_booking_status_logic",
            "dest": "alternative_appointment_display",
            "trigger": "booking_not_confirmed",
        },
        {
            "source": "alternative_appointment_display",
            "dest": "appointment_query_display",
            "trigger": "next",
        },
        {
            "source": "booking_confirmation_display",
            "dest": "further_assistance_display",
            "trigger": "next",
        },
        {
            "source": "further_assistance_display",
            "dest": "further_assistance_input",
            "trigger": "next",
        },
        {
            "source": "further_assistance_input",
            "dest": "process_further_assistance_logic",
            "trigger": "next",
        },
        {
            "source": "process_further_assistance_logic",
            "dest": "service_selection_display",
            "trigger": "next",
            "conditions": "needs_further_assistance",
        },
        {
            "source": "process_further_assistance_logic",
            "dest": "conclusion_display",
            "trigger": "next",
        },
        {
            "source": "further_assistance_fail_display",
            "dest": "further_assistance_display",
            "trigger": "next",
        },
        {
            "source": "conclusion_display",
            "dest": "end",
            "trigger": "next",
        },
    ]
    conditions = {
        "is_valid_service",
        "is_valid_date",
        "is_valid_time",
        "is_booking_confirmed",
        "needs_further_assistance",
    }
    output_variables = set()

    def __init__(self, send_message: callable, credentials: Dict[str, Any] = None):

        if credentials is None:
            credentials = {}

        self.credentials = {}

        self.credentials["AZURE_OPENAI_API_KEY"] = credentials.get(
            "AZURE_OPENAI_API_KEY"
        )
        if not self.credentials["AZURE_OPENAI_API_KEY"]:
            raise ValueError("Missing credential: AZURE_OPENAI_API_KEY")

        self.credentials["AZURE_OPENAI_API_VERSION"] = credentials.get(
            "AZURE_OPENAI_API_VERSION"
        )
        if not self.credentials["AZURE_OPENAI_API_VERSION"]:
            raise ValueError("Missing credential: AZURE_OPENAI_API_VERSION")

        self.credentials["AZURE_OPENAI_API_ENDPOINT"] = credentials.get(
            "AZURE_OPENAI_API_ENDPOINT"
        )
        if not self.credentials["AZURE_OPENAI_API_ENDPOINT"]:
            raise ValueError("Missing credential: AZURE_OPENAI_API_ENDPOINT")

        self.credentials["FAST_MODEL"] = credentials.get("FAST_MODEL")
        if not self.credentials["FAST_MODEL"]:
            raise ValueError("Missing credentials: FAST_MODEL")

        self.credentials["SLOW_MODEL"] = credentials.get("SLOW_MODEL")
        if not self.credentials["SLOW_MODEL"]:
            raise ValueError("Missing credentials: SLOW_MODEL")

        # print(self.credentials)

        self.plugins: Dict[str, AbstractFSM] = {}
        super().__init__(send_message=send_message)

    def standard_ask_again(self, message=None):
        self.status = Status.WAIT_FOR_ME
        if message is None:
            message = (
                "Sorry, I did not understand your question. Can you tell me again?"
            )
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def on_enter_select_language(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                message_data=MessageData(
                    body="Please select your preferred language.\nबंधु से संपर्क करने के लिए धन्यवाद!\nकृपया अपनी भाषा चुनें।"
                ),
                type=MessageType.TEXT,
                dialog="language",
                dest="channel",
            )
        )
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_welcome_message_display(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                message_data=MessageData(
                    body="Hello! Welcome to Car Wash Dealer. How can I assist you today?"
                ),
                type=MessageType.TEXT,
                dest="channel",
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Would you like to buy a car, service your car, test drive, buy accessories or parts, or get a warranty and protection plan?"

        options = [
            OptionsListType(id="1", title="Buy a Car"),
            OptionsListType(id="2", title="Service Car"),
            OptionsListType(id="3", title="Test Drive"),
            OptionsListType(id="4", title="Buy Accessories or Parts"),
            OptionsListType(id="5", title="Warranty and Protection Plan"),
        ]
        self.send_message(
            FSMOutput(
                type=MessageType.INTERACTIVE,
                message_data=MessageData(body=message),
                options_list=options,
                menu_selector="Service Select",
                menu_title="Service Select",
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_service_selection_logic(self):
        self.status = Status.WAIT_FOR_ME
        options = [
            OptionsListType(id="1", title="Buy a Car"),
            OptionsListType(id="2", title="Service Car"),
            OptionsListType(id="3", title="Test Drive"),
            OptionsListType(id="4", title="Buy Accessories or Parts"),
            OptionsListType(id="5", title="Warranty and Protection Plan"),
        ]
        task = "The user is asked to select a service from the options."

        result = OptionParser.parse(
            task,
            options,
            self.current_input,
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            model=self.credentials["FAST_MODEL"]
        )
        self.variables["service_id"] = result
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_fail_display(self):
        self.standard_ask_again(
            message="Sorry, I didn't get that. Please select one of the following options: Buy a Car, Service Car, Test Drive, Buy Accessories or Parts, or Warranty and Protection Plan."
        )

    def on_enter_appointment_query_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Great choice! When would you like to book the appointment? Please provide the date you would be interested?"
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def on_enter_date_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_date_logic(self):
        self.status = Status.WAIT_FOR_ME
        result = LLMManager.llm(
            messages=[
                LLMManager.sm(
                    "The user provides a date, convert it into a format of YYYY-MM-DD. If the date provided is wrong and could not be decided return None. Based on the user's input, return the output in json format. {'appointment_date': <date>}. Current time is " + str(datetime.now())
                ),
                LLMManager.um(self.current_input),
            ],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            response_format={"type": "json_object"},
            model=self.credentials["SLOW_MODEL"]
        )
        result = json.loads(result)
        self.variables["appointment_date"] = result["appointment_date"]
        self.status = Status.MOVE_FORWARD

    def on_enter_appointment_date_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.standard_ask_again(
            message="Sorry, I didn't get that. Please provide the date in the format YYYY-MM-DD."
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_appointment_time_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.standard_ask_again(
            message="Sorry, I didn't get that. Please select one of the following options: Morning, Afternoon, or Evening."
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_get_time_of_day_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "What time of day would you prefer? Morning, afternoon, or evening?"
        slots = [
            OptionsListType(id="1", title="Morning"),
            OptionsListType(id="2", title="Afternoon"),
            OptionsListType(id="3", title="Evening"),
        ]
        self.send_message(
            FSMOutput(
                type=MessageType.INTERACTIVE,
                message_data=MessageData(body=message),
                options_list=slots,
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_time_of_day_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_time_of_day_logic(self):
        self.status = Status.WAIT_FOR_ME
        valid_times = ["morning", "afternoon", "evening"]
        slots = [
            OptionsListType(id="1", title="Morning"),
            OptionsListType(id="2", title="Afternoon"),
            OptionsListType(id="3", title="Evening"),
        ]
        task = "The user is asked to select a time of day from the options."
        result = OptionParser.parse(
            task,
            slots,
            self.current_input,
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            model=self.credentials["FAST_MODEL"]
        )
        self.variables["appointment_id"] = result
        self.status = Status.MOVE_FORWARD

    def availability_plugin(self):
        return {
            "error_code": 400,
            "booking_status": "confirmed",
            "appointment_image": "https://d27jswm5an3efw.cloudfront.net/app/uploads/2019/08/image-url-3.jpg",
        }

    def on_enter_check_availability_plugin(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                type=MessageType.TEXT,
                message_data=MessageData(
                    body="Checking availability for the requested date and time..."
                ),
            )
        )

        response = self.availability_plugin()
        self.variables["booking_status"] = response["booking_status"]
        self.variables["appointment_image"] = response["appointment_image"]
        self.variables["error_code"] = response["error_code"]
        self.status = Status.MOVE_FORWARD

    def on_enter_check_booking_status_logic(self):
        self.status = Status.WAIT_FOR_ME
        if self.variables["booking_status"] == "confirmed":
            self.trigger("booking_confirmed")
        else:
            self.trigger("booking_not_confirmed")

    def on_enter_booking_confirmation_display(self):
        self.status = Status.WAIT_FOR_ME
        message = f"Your appointment has been successfully booked for {self.variables['service_selection']} on {self.variables['appointment_date']} at {self.variables['time_in_hr']}."
        self.send_message(
            FSMOutput(
                type=MessageType.IMAGE,
                message_data=MessageData(body=message),
                media_url=self.variables["appointment_image"],
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_alternative_appointment_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "The requested date and time are not available. Please provide another date and time for your appointment."
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_further_assistance_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Is there anything else I can help you with today?"
        options = [
            OptionsListType(id="1", title="Yes"),
            OptionsListType(id="2", title="No"),
        ]
        self.send_message(
            FSMOutput(
                type=MessageType.INTERACTIVE,
                message_data=MessageData(body=message),
                options_list=options,
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_further_assistance_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_further_assistance_logic(self):
        self.status = Status.WAIT_FOR_ME
        options = [
            OptionsListType(id="1", title="Yes"),
            OptionsListType(id="2", title="No"),
        ]
        result = OptionParser.parse(
            "The user provides a response to the 'Is there anything else I can help you with today?'.",
            options,
            self.current_input,
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            model=self.credentials["FAST_MODEL"]
        )
        if result == "1":
            self.variables["further_assistance"] = "yes"
        else:
            self.variables["further_assistance"] = "no"
        self.status = Status.MOVE_FORWARD

    def on_enter_further_assistance_fail_display(self):
        self.standard_ask_again(
            message="Sorry, I didn't get that. Please select one of the following options: Yes or No."
        )

    def on_enter_conclusion_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Thank you for choosing Car Wash Dealer. Have a great day!"
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def is_valid_service(self):
        valid_services = [
            "Buy a Car",
            "Service Car",
            "Test Drive",
            "Buy Accessories or Parts",
            "Warranty and Protection Plan",
        ]
        if (
            self.variables["service_id"]
            and self.variables["service_id"].isnumeric()
            and int(self.variables["service_id"]) <= 5
        ):
            valid_services = [service.title() for service in valid_services]
            index = int(self.variables["service_id"]) - 1
            self.variables["service_selection"] = valid_services[index]
            self.variables["service_selection"] = (
                self.variables["service_selection"].strip().title()
            )
            return self.variables["service_selection"] in valid_services
        return False

    def is_valid_date(self):
        if self.variables["appointment_date"]:
            try:
                datetime.strptime(
                    self.variables["appointment_date"], "%Y-%m-%d")
                return True
            except ValueError:
                return False
        return False

    def is_valid_time(self):
        if (
            self.variables["appointment_id"]
            and self.variables["appointment_id"].isnumeric()
            and int(self.variables["appointment_id"]) <= 3
        ):
            valid_times = ["morning", "afternoon", "evening"]
            self.variables["appointment_time"] = valid_times[
                int(self.variables["appointment_id"]) - 1
            ]

            if self.variables["appointment_time"] in valid_times:
                self.variables["time_in_hr"] = {
                    "morning": "09:00:00",
                    "afternoon": "13:00:00",
                    "evening": "17:00:00",
                }[self.variables["appointment_time"]]
                return True
            return False
        return False

    def on_enter_plugin_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                message_data=MessageData(
                    body="Sorry, I am unable to process your request at the moment, error while plugin call. Please try again later.\n Note this is expected behaviour as the plugin returns positive or negative values on random."
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def is_booking_confirmed(self):
        return self.variables["booking_status"] == "confirmed"

    def needs_further_assistance(self):
        return self.variables["further_assistance"] == "yes"

    def is_error_code_200(self):
        return self.variables["error_code"] == 200

    def is_error_code_400(self):
        return self.variables["error_code"] == 400

    def is_error_code_500(self):
        return self.variables["error_code"] == 500

    def is_error_code_404(self):
        return self.variables["error_code"] == 404
