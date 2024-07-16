import re
from pydantic import BaseModel
from typing import Dict, Any, Optional, Type
from jb_manager_bot import (
    AbstractFSM
    )

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

        self.credentials["OPENAI_API_KEY"] = credentials.get("OPENAI_API_KEY")
        if not self.credentials["OPENAI_API_KEY"]:
            raise ValueError("Missing credential: OPENAI_API_KEY")
        
        if not credentials.get("FAST_MODEL"):
            raise ValueError("Missing credential: FAST_MODEL")
        self.credentials["FAST_MODEL"] = credentials.get("FAST_MODEL")

        if not credentials.get("SLOW_MODEL"):
            raise ValueError("Missing credential: SLOW_MODEL")
        self.credentials["SLOW_MODEL"] = credentials.get("SLOW_MODEL")

        self.plugins: Dict[str, AbstractFSM] = {}
        self.variables = self.variable_names()
        super().__init__(send_message=send_message)
        # print(self.variables.__dict__)

    def on_enter_language_selection(self):
        self._on_enter_select_language()

    def on_enter_welcome_message_display(self):
        self._on_enter_display(
            message="Welcome to the Car Dealer Bot! How can I help you today?"
        )

    def on_enter_service_selection_display(self):
        self._on_enter_display(
            message="Would you like to buy a car, service your car, test drive, buy accessories or parts, or get a warranty and protection plan?",
            options=[
                "Buy a Car",
                "Service Car",
                "Test Drive",
                "Buy Accessories or Parts",
                "Warranty and Protection Plan",
            ],
        )

    def on_enter_service_selection_input(self):
        self._on_enter_empty_input()

    def on_enter_service_selection_logic(self):
        self._on_enter_input_logic(
            message="Please select one of the following options:",
            write_var="selected_service",
            options=[
                "Buy a Car",
                "Service Car",
                "Test Drive",
                "Buy Accessories or Parts",
                "Warranty and Protection Plan",
            ],
            validation="selected_service in ['Buy a Car', 'Service Car', 'Test Drive', 'Buy Accessories or Parts', 'Warranty and Protection Plan']",
        )

    def on_enter_service_selection_fail(self):
        self.status = Status.WAIT_FOR_ME
        variable_name = "fail_service_count"
        expression = "fail_service_count + 1"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x + 1
        self._on_enter_assign(
            variable_name,
            validation,
        )

        self.status = Status.MOVE_FORWARD

    def on_enter_service_selection_task_fail_verify(self):
        self._on_enter_empty_branching()

    def is_service_fail_count_less_than_3(self):
        variable_name = "fail_service_count"
        expression = "fail_service_count < 3"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x < 3
        return self._validate_method(variable_name, validation)

    def is_service_fail_count_3(self):
        variable_name = "fail_service_count"
        expression = "fail_service_count >= 3"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x >= 3
        return self._validate_method(variable_name, validation)

    def on_enter_service_selection_fail_display(self):
        self._on_enter_display(
            message="Sorry, I didn't understand that. Please select one of the following options:",
        )

    def on_enter_date_display(self):
        self._on_enter_display(
            message="Please enter the date you would like to schedule your appointment (YYYY-MM-DD):"
        )

    def on_enter_date_input(self):
        self._on_enter_empty_input()

    def on_enter_date_logic(self):
        self._on_enter_input_logic(
            write_var="appointment_date",
            validation="re.match(r'^\d{4}-\d{2}-\d{2}$', appointment_date) is not None",
        )

    def on_enter_date_fail_display(self):
        self._on_enter_display(
            message="Sorry, I didn't understand that. Please enter the date you would like to schedule your appointment (YYYY-MM-DD):"
        )

    def on_enter_time_display(self):
        self._on_enter_display(
            message="Please enter the time of day you would like to schedule your appointment (Morning, Afternoon, Evening):",
            options=["Morning", "Afternoon", "Evening"],
        )

    def on_enter_time_input(self):
        self._on_enter_empty_input()

    def on_enter_time_logic(self):
        self._on_enter_input_logic(
            write_var="appointment_time",
            options=["Morning", "Afternoon", "Evening"],
            validation="appointment_time in ['Morning', 'Afternoon', 'Evening']",
        )

    def on_enter_time_fail_display(self):
        self._on_enter_display(
            "Sorry, I didn't understand that. Please enter the time of day you would like to schedule your appointment (Morning, Afternoon, Evening):"
        )

    def on_enter_check_availability_plugin(self):
        self._on_enter_plugin(
            plugin=availability_plugin,
            input_variables={
                "SELECTED_SERVICE": "selected_service",
                "APPOINTMENT_DATE": "appointment_date",
                "APPOINTMENT_TIME": "appointment_time",
            },
            output_variables={
                "booking_status": "booking_status",
                "appointment_image": "appointment_image",
                # "error_code": "error_code",
            },
            message="Checking availability for your appointment...",
        )

    def on_enter_plugin_fail_display(self):
        self._on_enter_display(
            message="Sorry, We couldn't complete your booking. Apologies, Please try again after sometime."
        )

    def on_enter_check_booking_status_logic(self):
        self._on_enter_empty_branching()

    def on_enter_booking_pending_display(self):
        self._on_enter_display(
            message="Sorry, We couldn't complete your booking. Apologies, Please try again after sometime."
        )

    def on_enter_booking_confirmation_display(self):
        self._on_enter_display(
            message="Your appointment has been confirmed! Please check your email for more details.",
        )

    def on_enter_further_assistance_display(self):
        self._on_enter_display(
            message="Do you need further assistance?",
            options=["Yes", "No"],
        )

    def on_enter_further_assistance_input(self):
        self._on_enter_empty_input()

    def on_enter_further_assistance_logic(self):
        self._on_enter_input_logic(
            write_var="further_assistance",
            options=["Yes", "No"],
            validation="isinstance(further_assistance, str) and re.match(r'^(Yes|No)$', further_assistance) is not None",
        )

    def on_enter_further_assistance_fail_display(self):
        self._on_enter_display(
            message="Sorry, I didn't understand that. Please select one of the following options: Yes or No",
        )

    def on_enter_further_assistance_verify(self):
        self._on_enter_empty_branching()

    def on_enter_conclusion_display(self):
        self._on_enter_display(
            message="Thank you for using the Car Dealer Bot! Have a great day!"
        )

    def is_valid_service(self):
        variable_name = "selected_service"
        expression = "selected_service in ['Buy a Car', 'Service Car', 'Test Drive', 'Buy Accessories or Parts', 'Warranty and Protection Plan']"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x in [
            "Buy a Car",
            "Service Car",
            "Test Drive",
            "Buy Accessories or Parts",
            "Warranty and Protection Plan",
        ]
        return self._validate_method(variable_name, validation)

    def is_valid_date(self):
        variable_name = "appointment_date"
        expression = ("re.match(r'^\d{4}-\d{2}-\d{2}$', appointment_date) is not None",)
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: re.match(r"^\d{4}-\d{2}-\d{2}$", x) is not None
        return self._validate_method(variable_name, validation)

    def is_valid_time(self):
        variable_name = "appointment_time"
        expression = "appointment_time in ['Morning', 'Afternoon', 'Evening']"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x in ["Morning", "Afternoon", "Evening"]
        return self._validate_method(variable_name, validation)

    def is_booking_confirmed(self):
        variable_name = "booking_status"
        expression = "booking_status == 'confirmed'"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x == "confirmed"
        return self._validate_method(variable_name, validation)

    def is_booking_pending(self):
        variable_name = "booking_status"
        expression = "booking_status != 'confirmed'"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x != "confirmed"
        return self._validate_method(variable_name, validation)

    def is_error_code_200(self):
        return self._plugin_error_code_validation(200)

    def is_further_assistance_valid(self):
        variable = "further_assistance"
        expression = "isinstance(further_assistance, str) and re.match(r'^(Yes|No)$', further_assistance) is not None"
        # validation = lambda x: {expression.replace(variable, "x")}
        validation = (
            lambda x: isinstance(x, str) and re.match(r"^(Yes|No)$", x) is not None
        )
        return self._validate_method(variable, validation)

    def is_further_assistance(self):
        variable_name = "further_assistance"
        expression = "further_assistance == 'Yes'"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x == "Yes"
        return self._validate_method(variable_name, validation)

    def is_not_further_assistance(self):
        variable_name = "further_assistance"
        expression = "further_assistance == 'No'"
        # validation = lambda x: {expression.replace(variable_name, "x")}
        validation = lambda x: x == "No"
        return self._validate_method(variable_name, validation)

    def is_error_code_400(self):
        return self._plugin_error_code_validation(400)

    def is_error_code_500(self):
        return self._plugin_error_code_validation(500)

    def is_error_code_404(self):
        return self._plugin_error_code_validation(404)
