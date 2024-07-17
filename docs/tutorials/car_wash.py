import re
from pydantic import BaseModel
from typing import Dict, Any, Optional, Type
from jb_manager_bot import AbstractFSM
from jb_manager_bot.data_models import (
    FSMOutput,
    Message,
    MessageType,
    Status,
    FSMIntent,
    TextMessage,
    ListMessage,
    ButtonMessage,
    Option,
    ImageMessage,
)
from datetime import datetime
from jb_manager_bot.parsers import Parser, OptionParser


# example plugin
def availability_plugin(SELECTED_SERVICE, APPOINTMENT_DATE, APPOINTMENT_TIME):
    return {
        "error_code": 200,
        "booking_status": "confirmed",
        "appointment_image": "https://d27jswm5an3efw.cloudfront.net/app/uploads/2019/08/image-url-3.jpg",
    }


# Variables are defined here
class CarWashDealerVariables(BaseModel):
    selected_service: Optional[str] = None
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None
    availability_status: Optional[str] = None
    booking_message: Optional[str] = None
    further_assistance: Optional[str] = None
    booking_status: Optional[str] = None
    appointment_image: Optional[str] = None
    error_code: Optional[int] = None
    fail_service_count: int = 0


class CarWashDealerFSM(AbstractFSM):

    states = [
        "zero",
        "language_selection",
        "welcome_message_display",
        "service_selection_display",
        "service_selection_input",
        "service_selection_logic",
        "service_selection_fail",
        "service_selection_task_fail_verify",
        "service_selection_fail_display",
        "date_display",
        "date_input",
        "date_logic",
        "time_display",
        "time_input",
        "time_logic",
        "date_fail_display",
        "time_fail_display",
        "check_availability_plugin",
        "plugin_fail_display",
        "check_booking_status_logic",
        "booking_confirmation_display",
        "booking_pending_display",
        "further_assistance_display",
        "further_assistance_input",
        "further_assistance_logic",
        "further_assistance_fail_display",
        "further_assistance_verify",
        "conclusion_display",
        "end",
    ]
    transitions = [
        {"source": "zero", "dest": "language_selection", "trigger": "next"},
        {
            "source": "language_selection",
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
            "dest": "date_display",
            "trigger": "next",
            "conditions": "is_valid_service",
        },
        {
            "source": "service_selection_logic",
            "dest": "service_selection_fail",
            "trigger": "next",
        },
        {
            "source": "service_selection_fail",
            "dest": "service_selection_task_fail_verify",
            "trigger": "next",
        },
        {
            "source": "service_selection_task_fail_verify",
            "dest": "service_selection_display",
            "trigger": "next",
            "conditions": "is_service_fail_count_less_than_3",
        },
        {
            "source": "service_selection_task_fail_verify",
            "dest": "end",
            "trigger": "next",
            "conditions": "is_service_fail_count_3",
        },
        {
            "source": "date_display",
            "dest": "date_input",
            "trigger": "next",
        },
        {
            "source": "date_input",
            "dest": "date_logic",
            "trigger": "next",
        },
        {
            "source": "date_logic",
            "dest": "time_display",
            "trigger": "next",
            "conditions": "is_valid_date",
        },
        {
            "source": "date_logic",
            "dest": "date_fail_display",
            "trigger": "next",
        },
        {
            "source": "date_fail_display",
            "dest": "date_display",
            "trigger": "next",
        },
        {
            "source": "time_display",
            "dest": "time_input",
            "trigger": "next",
        },
        {
            "source": "time_input",
            "dest": "time_logic",
            "trigger": "next",
        },
        {
            "source": "time_logic",
            "dest": "check_availability_plugin",
            "trigger": "next",
            "conditions": "is_valid_time",
        },
        {
            "source": "time_logic",
            "dest": "time_fail_display",
            "trigger": "next",
        },
        {
            "source": "time_fail_display",
            "dest": "time_display",
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
            "dest": "end",
            "trigger": "next",
        },
        {
            "source": "check_booking_status_logic",
            "dest": "booking_confirmation_display",
            "trigger": "next",
            "conditions": "is_booking_confirmed",
        },
        {
            "source": "check_booking_status_logic",
            "dest": "booking_pending_display",
            "trigger": "next",
        },
        {
            "source": "booking_pending_display",
            "dest": "end",
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
            "dest": "further_assistance_logic",
            "trigger": "next",
        },
        {
            "source": "further_assistance_logic",
            "dest": "further_assistance_verify",
            "trigger": "next",
            "conditions": "is_further_assistance_valid",
        },
        {
            "source": "further_assistance_logic",
            "dest": "further_assistance_fail_display",
            "trigger": "next",
        },
        {
            "source": "further_assistance_verify",
            "dest": "service_selection_display",
            "trigger": "next",
            "conditions": "is_further_assistance",
        },
        {
            "source": "further_assistance_verify",
            "dest": "conclusion_display",
            "trigger": "next",
            "conditions": "is_not_further_assistance",
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
        "is_booking_pending",
        "is_error_code_200",
        "is_error_code_400",
        "is_error_code_500",
        "is_error_code_404",
        "is_further_assistance_valid",
        "is_further_assistance",
        "is_not_further_assistance",
    }
    output_variables = set()
    variable_names = CarWashDealerVariables

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

        if not credentials.get("FAST_MODEL"):
            raise ValueError("Missing credential: FAST_MODEL")
        self.credentials["FAST_MODEL"] = credentials.get("FAST_MODEL")

        if not credentials.get("SLOW_MODEL"):
            raise ValueError("Missing credential: SLOW_MODEL")
        self.credentials["SLOW_MODEL"] = credentials.get("SLOW_MODEL")

        self.plugins: Dict[str, AbstractFSM] = {}
        self.variables = self.variable_names()
        super().__init__(send_message=send_message)
    
    def standard_ask_again(self, message=None):
        self.status = Status.WAIT_FOR_ME
        if message is None:
            message = (
                "Sorry, I did not understand your question. Can you tell me again?"
            )
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT, text=TextMessage(body=message)
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_language_selection(self):
        self._on_enter_select_language()

    def on_enter_welcome_message_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Hello! Welcome to Car Wash Dealer. How can I assist you today?"
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT, text=TextMessage(body=message)
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Would you like to buy a car, service your car, test drive, buy accessories or parts, or get a warranty and protection plan?"

        options = [
            Option(option_id="1", option_text="Buy a Car"),
            Option(option_id="2", option_text="Service Car"),
            Option(option_id="3", option_text="Test Drive"),
            Option(option_id="4", option_text="Buy Accessories or Parts"),
            Option(option_id="5", option_text="Warranty and Protection Plan"),
        ]
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.OPTION_LIST,
                    option_list=ListMessage(
                        body=message,
                        header="",
                        footer="",
                        button_text="Service Select",
                        list_title="Service Select",
                        options=options,
                    ),
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_service_selection_logic(self):
        self.status = Status.WAIT_FOR_ME
        options = [
            Option(option_id="1", option_text="Buy a Car"),
            Option(option_id="2", option_text="Service Car"),
            Option(option_id="3", option_text="Test Drive"),
            Option(option_id="4", option_text="Buy Accessories or Parts"),
            Option(option_id="5", option_text="Warranty and Protection Plan"),
        ]
        task = "The user is asked to select a service from the options."
        result = Parser.parse_user_input(
            task,
            options,
            self.current_input,
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            model=self.credentials["FAST_MODEL"],
        )

        if options:
            result = result["id"]
            if result.isdigit():
                result = options[int(result) - 1].option_text

        else:
            result = result["result"]
        try:
            # update the pydantic variable with the result
            setattr(self.variables, "selected_service", result)
        except Exception as e:
            setattr(self.variables, "selected_service", None)
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_fail(self):
        self.status = Status.WAIT_FOR_ME
        value = self.variables.fail_service_count
        setattr(self.variables, "fail_service_count", value + 1)
        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_task_fail_verify(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.MOVE_FORWARD

    def is_service_fail_count_less_than_3(self):
        if self.variables.fail_service_count < 3:
            return True
        return False

    def is_service_fail_count_3(self):
        if self.variables.fail_service_count == 3:
            return True
        return False

    def on_enter_service_selection_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Sorry, I didn't get that. Please select one of the following options: Buy a Car, Service Car, Test Drive, Buy Accessories or Parts, or Warranty and Protection Plan."
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT, text=TextMessage(body=message)
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_date_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Great choice! When would you like to book the appointment? Please provide the date you would be interested?"
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT, text=TextMessage(body=message)
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_date_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_date_logic(self):
    def on_enter_date_logic(self):
        self.status = Status.WAIT_FOR_ME
        task = f"The user provides a date or day, convert it into a format of YYYY-MM-DD. Today's date is {datetime.now().strftime("%Y-%m-%d")} & Day is {datetime.now().strftime("%A")}Format and modify the user input into the format required and if you could not be decide return None. Based on the user's input, return the output in json format: {{'result': <input>}}."

        result = Parser.parse_user_input(
            task,
            options=None,
            user_input=self.current_input,
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            model=self.credentials["FAST_MODEL"],
        )
        result = result["result"]
        try:
            setattr(self.variables, "appointment_date", result)
        except Exception as e:
            setattr(self.variables, "appointment_date", None)
        self.status = Status.MOVE_FORWARD

    def on_enter_date_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.standard_ask_again(
            message="Sorry, I didn't get that. Please provide the date in the format YYYY-MM-DD."
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_time_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "What time of day would you prefer? Morning, afternoon, or evening?"
        slots = [
            Option(option_id="1", option_text="Morning"),
            Option(option_id="2", option_text="Afternoon"),
            Option(option_id="3", option_text="Evening"),
        ]
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.BUTTON,
                    button=ButtonMessage(
                        body=message,
                        header="",
                        footer="",
                        options=slots,
                    ),
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_time_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_time_logic(self):
        self.status = Status.WAIT_FOR_ME
        valid_times = ["morning", "afternoon", "evening"]
        slots = [
            Option(option_id="1", option_text="Morning"),
            Option(option_id="2", option_text="Afternoon"),
            Option(option_id="3", option_text="Evening"),
        ]
        task = "The user is asked to select a time of day from the options."
        result = OptionParser.parse(
            task,
            slots,
            self.current_input,
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            model=self.credentials["FAST_MODEL"],
        )
        if result.isdigit():
            result = slots[int(result) - 1].option_text
            setattr(self.variables, "appointment_time", result)
        else:
            setattr(self.variables, "appointment_time", None)
        self.status = Status.MOVE_FORWARD

    def on_enter_time_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.standard_ask_again(
            message="Sorry, I didn't get that. Please select one of the following options: Morning, Afternoon, or Evening."
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_check_availability_plugin(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT,
                    text=TextMessage(
                        body="Checking availability for the requested date and time..."
                    ),
                ),
            )
        )

        response = availability_plugin(
            self.variables.selected_service,
            self.variables.appointment_date,
            self.variables.appointment_time,
        )
        self.variables.booking_status = response["booking_status"]
        self.variables.appointment_image = response["appointment_image"]
        self.variables.error_code = response["error_code"]
        self.status = Status.MOVE_FORWARD

    def on_enter_plugin_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.standard_ask_again(
            "Sorry, We couldn't complete your booking. Apologies, Please try again after sometime."
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_check_booking_status_logic(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.MOVE_FORWARD

    def on_enter_booking_pending_display(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT,
                    text=TextMessage(
                        body="Sorry, We couldn't complete your booking. Apologies, Please try again after sometime."
                    ),
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_booking_confirmation_display(self):
        self._on_enter_display(
            message="Your appointment has been confirmed! Please check your email for more details.",
        )
        self.status = Status.WAIT_FOR_ME
        message = f"Your appointment has been successfully booked for {self.variables.selected_service} on {self.variables.appointment_date} at {self.variables.appointment_time}."
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.IMAGE,
                    image=ImageMessage(
                        url=self.variables.appointment_image, caption=message
                    ),
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_further_assistance_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Is there anything else I can help you with today?"
        options = [
            Option(option_id="1", option_text="Yes"),
            Option(option_id="2", option_text="No"),
        ]
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.BUTTON,
                    button=ButtonMessage(
                        body=message,
                        header="",
                        footer="",
                        options=options,
                    ),
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_further_assistance_input(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_further_assistance_logic(self):
        self.status = Status.WAIT_FOR_ME
        options = [
            Option(option_id="1", option_text="Yes"),
            Option(option_id="2", option_text="No"),
        ]
        result = OptionParser.parse(
            "The user provides a response to the 'Is there anything else I can help you with today?'.",
            options,
            self.current_input,
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            model=self.credentials["FAST_MODEL"],
        )
        if result == "1":
            self.variables.further_assistance = "Yes"
        else:
            self.variables.further_assistance = "No"
        self.status = Status.MOVE_FORWARD

    def on_enter_further_assistance_fail_display(self):
        self.status = Status.WAIT_FOR_ME
        self.standard_ask_again(
            "Sorry, I didn't understand that. Please select one of the following options: Yes or No"
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_further_assistance_verify(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.MOVE_FORWARD

    def on_enter_conclusion_display(self):
        self.status = Status.WAIT_FOR_ME
        message = "Thank you for choosing Car Wash Dealer. Have a great day!"
        self.send_message(
            FSMOutput(
                intent=FSMIntent.SEND_MESSAGE,
                message=Message(
                    message_type=MessageType.TEXT, text=TextMessage(body=message)
                ),
            )
        )
        self.status = Status.MOVE_FORWARD

    def is_valid_service(self):
        validation = lambda x: x in [
            "Buy a Car",
            "Service Car",
            "Test Drive",
            "Buy Accessories or Parts",
            "Warranty and Protection Plan",
        ]
        return validation(self.variables.selected_service)

    def is_valid_date(self):
        validation = lambda x: re.match(r"^\d{4}-\d{2}-\d{2}$", x) is not None
        return validation(self.variables.appointment_date)

    def is_valid_time(self):
        validation = lambda x: x in ["Morning", "Afternoon", "Evening"]
        return validation(self.variables.appointment_time)

    def is_booking_confirmed(self):
        validation = lambda x: x == "confirmed"
        return validation(self.variables.booking_status)

    def is_booking_pending(self):
        validation = lambda x: x != "confirmed"
        return validation(self.variables.booking_status)

    def is_error_code_200(self):
        if self.variables.error_code == 200:
            return True
        return False

    def is_further_assistance_valid(self):
        validation = (
            lambda x: isinstance(x, str) and re.match(r"^(Yes|No)$", x) is not None
        )
        return validation(self.variables.further_assistance)

    def is_further_assistance(self):
        validation = lambda x: x == "Yes"
        return validation(self.variables.further_assistance)

    def is_not_further_assistance(self):
        variable_name = "further_assistance"
        validation = lambda x: x == "No"
        return self._validate_method(variable_name, validation)

    def is_error_code_400(self):
        if self.variables.error_code == 400:
            return True
        return False

    def is_error_code_500(self):
        if self.variables.error_code == 500:
            return True
        return False

    def is_error_code_404(self):
        if self.variables.error_code == 404:
            return True
        return False
