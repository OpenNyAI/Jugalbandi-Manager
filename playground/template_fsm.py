import json
import random
from datetime import datetime
from typing import Any, Dict, Type

from jb_manager_bot import (AbstractFSM, FSMOutput, MessageData, MessageType,
                            OptionsListType, Status)
from jb_manager_bot.parsers import OptionParser
from jb_manager_bot.parsers.utils import LLMManager


def template_property_details():
    return {
        "property_details": [
            {
                "property_id": "p5",
                "city": "Mumbai",
                "Area": "Andheri",
                "locality": "Azad Nagar",
                "property_type": "Basti",
                "availability_start_date": "2024-01-15",
                "Available Until": "2024-07-30",
                "monthly_rent": 7000,
                "security_deposit": 14000,
                "Brokerage": 0,
                "Rooms": 1,
                "Total Occupancy": 4.0,
                "Kitchen": "yes",
                "Bathing": "private",
                "Toilet": "private",
                "Electricity": "govt",
            },
            {
                "property_id": "p2",
                "city": "Mumbai",
                "Area": "Andheri",
                "locality": "Azad Nagar",
                "property_type": "Basti",
                "availability_start_date": "2023-05-20",
                "Available Until": "2024-01-31",
                "monthly_rent": 8000,
                "security_deposit": 16000,
                "Brokerage": 0,
                "Rooms": 1,
                "Total Occupancy": 2.0,
                "Kitchen": "yes",
                "Bathing": "private",
                "Toilet": "common",
                "Electricity": "govt",
            },
            {
                "property_id": "p8",
                "city": "Mumbai",
                "Area": "Andheri",
                "locality": "Hanuman Nagar",
                "property_type": "Basti",
                "availability_start_date": "2023-08-04",
                "Available Until": "2025-04-30",
                "monthly_rent": 8500,
                "security_deposit": 17000,
                "Brokerage": 0,
                "Rooms": 1,
                "Total Occupancy": 4.0,
                "Kitchen": "yes",
                "Bathing": "private",
                "Toilet": "common",
                "Electricity": "govt"
            }
        ]
    }


class HousingAppFSM(AbstractFSM):
    """
    This is the main FSM class for the template Housing App project.
    """
    states = [
        "zero",
        "select_language",
        "ask_house_preferences",  # send the message -> Please provide your house preferences
        "input_ask_house_preferences",  # wait for input
        "generate_chunks",
        "process_ask_house_preferences",  # process the user input
        "ask_house_preference_again",  # send the message -> Couldn't understand; Goto input_ask_house_preferences 
        "ask_move_in_date",
        "input_ask_move_in_date",
        "process_ask_move_in_date",
        "confirm_house_preferences",
        "input_confirm_house_preferences",
        "process_confirm_house_preferences",
        "ask_for_selecting_house_option",
        "input_ask_for_selecting_house_option",
        "process_ask_for_selecting_house_option",
        "ask_for_confirming_property_visit",
        "input_ask_for_confirming_property_visit",
        "process_ask_for_confirming_property_visit",
        "ask_for_confirming_property_choice",
        "input_ask_for_confirming_property_choice",
        "process_ask_for_confirming_property_choice",
        "all_process_completed",
        "ask_move_in_date_again",
        "confirm_house_preferences_again",
        "booking_cancelled",
        "cancel_house_option",
        "end",
    ]
    transitions = [
        {
            "source": "process_ask_for_confirming_property_choice",
            "dest": "all_process_completed",
            "trigger": "next",
            "conditions": "is_booking_confirm",
        },
        {
            "source": "process_ask_for_confirming_property_choice",
            "dest": "booking_cancelled",
            "trigger": "next",
            "conditions": "is_cancelled_booking",
        },
        {
            "source": "process_ask_for_confirming_property_choice",
            "dest": "input_ask_for_confirming_property_choice",
            "trigger": "next",
            "conditions": "is_needing_more_time",
        },
        {
            "source": "process_ask_for_confirming_property_visit",
            "dest": "input_ask_for_confirming_property_visit",
            "trigger": "next",
            "conditions": "not_yet_done_property_visit",
        },
        {
            "source": "ask_for_selecting_house_option",
            "dest": "input_ask_for_selecting_house_option",
            "trigger": "next",
        },
        {
            "source": "input_ask_for_selecting_house_option",
            "dest": "process_ask_for_selecting_house_option",
            "trigger": "next",
        },
        {
            "source": "process_ask_for_selecting_house_option",
            "dest": "ask_for_confirming_property_visit",
            "trigger": "next",
            "conditions": "is_chosen_house_option"
        },
        {
            "source": "process_ask_for_selecting_house_option",
            "dest": "cancel_house_option",
            "trigger": "next",
            "conditions": "is_cancelled_house_option"
        },
        {
            "source": "process_confirm_house_preferences",
            "dest": "ask_for_selecting_house_option",
            "trigger": "next",
            "conditions": "is_valid_collected_preferences",
        },
        {
            "source": "process_confirm_house_preferences",
            "dest": "ask_house_preferences",
            "trigger": "next",
            "conditions": "is_invalid_collected_preferences",
        },
        {
            "source": "process_confirm_house_preferences",
            "dest": "confirm_house_preferences_again",
            "trigger": "next",
            "conditions": "is_invalid_input_on_collected_preference",
        },
        {
            "source": "process_ask_move_in_date",
            "dest": "ask_move_in_date_again",
            "trigger": "next",
            "conditions": "is_invalid_check_move_in_date",
        },
        {
            "source": "process_ask_for_confirming_property_visit",
            "dest": "ask_for_confirming_property_choice",
            "trigger": "next",
            "conditions": "completed_property_visit",
        },
        {
            "source": "process_ask_house_preferences",
            "dest": "ask_house_preference_again",
            "trigger": "next",
            "conditions": "is_invalid_check_house_preferences",
        },
        {
            "source": "zero",
            "dest": "select_language",
            "trigger": "next"
        },
        {
            "source": "select_language",
            "dest": "ask_house_preferences",
            "trigger": "next",
        },
        {
            "source": "ask_house_preferences",
            "dest": "input_ask_house_preferences",
            "trigger": "next",
        },
        {
            "source": "input_ask_house_preferences",
            "dest": "generate_chunks",
            "trigger": "next",
        },
        {
            "source": "generate_chunks",
            "dest": "process_ask_house_preferences",
            "trigger": "next",
        },
        {
            "source": "process_ask_house_preferences",
            "dest": "ask_move_in_date",
            "trigger": "next",
        },
        {
            "source": "ask_move_in_date",
            "dest": "input_ask_move_in_date",
            "trigger": "next",
        },
        {
            "source": "input_ask_move_in_date",
            "dest": "process_ask_move_in_date",
            "trigger": "next",
        },
        {
            "source": "process_ask_move_in_date",
            "dest": "confirm_house_preferences",
            "trigger": "next",
        },
        {
            "source": "confirm_house_preferences",
            "dest": "input_confirm_house_preferences",
            "trigger": "next",
        },
        {
            "source": "input_confirm_house_preferences",
            "dest": "process_confirm_house_preferences",
            "trigger": "next",
        },
        {
            "source": "ask_for_confirming_property_visit",
            "dest": "input_ask_for_confirming_property_visit",
            "trigger": "next",
        },
        {
            "source": "input_ask_for_confirming_property_visit",
            "dest": "process_ask_for_confirming_property_visit",
            "trigger": "next",
        },
        {
            "source": "ask_for_confirming_property_choice",
            "dest": "input_ask_for_confirming_property_choice",
            "trigger": "next",
        },
        {
            "source": "input_ask_for_confirming_property_choice",
            "dest": "process_ask_for_confirming_property_choice",
            "trigger": "next",
        },
        {
            "source": "all_process_completed",
            "dest": "end",
            "trigger": "next"
        },
        {
            "source": "ask_house_preference_again",
            "dest": "input_ask_house_preferences",
            "trigger": "next",
        },
        {
            "source": "ask_move_in_date_again",
            "dest": "input_ask_move_in_date",
            "trigger": "next",
        },
        {
            "source": "confirm_house_preferences_again",
            "dest": "input_confirm_house_preferences",
            "trigger": "next",
        },
        {
            "source": "cancel_house_option",
            "dest": "end",
            "trigger": "next"
        },
        {
            "source": "booking_cancelled",
            "dest": "end",
            "trigger": "next"
        },
    ]
    conditions = {
        "is_invalid_check_move_in_date",
        "is_valid_collected_preferences",
        "is_cancelled_booking",
        "is_cancelled_house_option",
        "is_chosen_house_option",
        "is_booking_confirm",
        "completed_property_visit",
        "is_invalid_collected_preferences",
        "is_search_cancelled",
        "not_yet_done_property_visit",
        "is_needing_more_time",
        "is_invalid_input_on_collected_preference",
        "is_invalid_check_house_preferences",
    }
    output_variables = set()

    def __init__(self, send_message: callable, credentials: Dict[str, Any] = None):

        if credentials is None:
            credentials = {}

        self.credentials = {}
        self.credentials["OPENAI_API_KEY"] = credentials.get("OPENAI_API_KEY")
        if not self.credentials["OPENAI_API_KEY"]:
            raise ValueError("Missing credential: OPENAI_API_KEY")
        self.credentials["AZURE_OPENAI_API_KEY"] = credentials.get("AZURE_OPENAI_API_KEY")
        if not self.credentials["AZURE_OPENAI_API_KEY"]:
            raise ValueError("Missing credential: AZURE_OPENAI_API_KEY")
        self.credentials["AZURE_OPENAI_API_VERSION"] = credentials.get("AZURE_OPENAI_API_VERSION")
        if not self.credentials["AZURE_OPENAI_API_VERSION"]:
            raise ValueError("Missing credential: AZURE_OPENAI_API_VERSION")
        self.credentials["AZURE_OPENAI_API_ENDPOINT"] = credentials.get("AZURE_OPENAI_API_ENDPOINT")
        if not self.credentials["AZURE_OPENAI_API_ENDPOINT"]:
            raise ValueError("Missing credential: AZURE_OPENAI_API_ENDPOINT")

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

    def on_enter_greet_user(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                message_data=MessageData(body="Welcome to the Housing App!"),
                type=MessageType.TEXT,
                dest="channel",
            )
        )
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

    def on_enter_ask_house_preferences(self):
        self.status = Status.WAIT_FOR_ME
        message_head = "Please send us text or voice note with your house preferences."
        message_body = "\n\nTell us:\n• What kind of stay? (room/sleeping space/entire property)\n• City\n• Monthly rent budget"
        self.send_message(
            FSMOutput(message_data=MessageData(body=message_head + message_body))
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_input_ask_house_preferences(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_generate_chunks(self):
        self.status = Status.WAIT_FOR_ME
        self.variables["query"]=self.current_input
        self.send_message(
            FSMOutput(
                message_data=MessageData(body=self.variables["query"]),
                dest="rag"
            )
        )
        self.status = Status.WAIT_FOR_CALLBACK

    def on_enter_process_ask_house_preferences(self):
        self.status = Status.WAIT_FOR_ME
        chunks = self.current_input
        chunks = json.loads(chunks)["chunks"]
        knowledge = "\n".join([row["chunk"] for row in chunks])

        result = LLMManager.llm(
            messages=[
                    LLMManager.sm(
                        "The user provides a preference to book a house for rent. Extract the number of rooms , type of room, budget and location from the input. Return the output as a json object. The description of the output fields are as follows:\n 1. number_of_rooms: The number of rooms the user wants to book. \n 2. type_of_room: Choice of room either from 'room' or 'sleeping space' or 'entire property'. \n 3. budget: The budget the user has for the booking. \n 4. location: The location the user wants to book the house. "
                    ),
                    LLMManager.um(self.current_input),
            ],
            openai_api_key=self.credentials["OPENAI_API_KEY"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            response_format={"type": "json_object"},
            model="gpt4"
        )
        result = json.loads(result)
        number_of_rooms = (
            result.get("number_of_rooms") if result.get("number_of_rooms") else "1"
        )
        type_of_room = (
            result.get("type_of_room") if result.get("type_of_room") else "room"
        )
        budget = result.get("budget")
        location = result.get("location")
        self.variables["house_preferences"] = {
            "number_of_rooms": str(number_of_rooms),
            "type_of_room": type_of_room,
            "budget": str(budget),
            "location": location,
        }
        self.status = Status.MOVE_FORWARD

    def on_enter_ask_house_preference_again(self):
        self.standard_ask_again()

    def on_enter_ask_move_in_date(self):
        self.status = Status.WAIT_FOR_ME
        message = "Thanks! When do you want to move?\nPlease provide day and month."
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def on_enter_input_ask_move_in_date(self):
        self.status = Status.WAIT_FOR_ME
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_ask_move_in_date(self):
        numeric_to_month_mapping = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
        self.status = Status.WAIT_FOR_ME
        result = LLMManager.llm(
            messages=[
                    LLMManager.sm(
                        "Given a text that includes a date, extract the day and month from the date mentioned within the text. The day and month should be represented as numbers. The output should be in JSON format, indicating the day and month as separate fields. Input: A string of text that includes a date. Task: Identify and extract the day and month from the date mentioned in the input text. Output Format: { 'day': <Extracted day as a number>, 'month': <Extracted month as a number> } Example: Input: 'We are planning a meeting on 15th March 2023.' Output: { 'day': 15, 'month': 3 } Ensure the solution is robust enough to handle different date formats mentioned in the text and extract the day and month accurately. "
                    ),
                    LLMManager.um(self.current_input),
            ],
            openai_api_key=self.credentials["OPENAI_API_KEY"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            response_format={"type": "json_object"},
            model=os.getenv("OPENAI_API_DEPLOYMENT_NAME")
        )
        result = json.loads(result)
        day = result.get("day")
        month = result.get("month")
        self.variables["house_preferences"]["move_in_preference"] = {
            "day": day,
            "month": numeric_to_month_mapping[int(month)],
        }
        self.status = Status.MOVE_FORWARD

    def on_enter_ask_move_in_date_again(self):
        self.standard_ask_again()

    def on_enter_confirm_house_preferences(self):
        self.status = Status.WAIT_FOR_ME
        services = [
            OptionsListType(id="1", title="✅ Yes!"),
            OptionsListType(id="2", title="❌ No!"),
        ]
        number_of_rooms = self.variables["house_preferences"].get("number_of_rooms")
        type_of_room = self.variables["house_preferences"].get("type_of_room")
        budget = self.variables["house_preferences"].get("budget")
        location = self.variables["house_preferences"].get("location")
        day = self.variables["house_preferences"]["move_in_preference"].get("day")
        month = self.variables["house_preferences"]["move_in_preference"].get("month")

        message = f"As I understood it, you want {number_of_rooms} {type_of_room} in {location}, your monthly rent budget is Rs. {budget} and you want to move by {day} {month}. Is this correct?"
        self.send_message(
            FSMOutput(
                message_data=MessageData(
                    body=message,
                    header="Thank you for using the Housing App",
                    footer="Choose an option below",
                ),
                type=MessageType.INTERACTIVE,
                options_list=services,
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_input_confirm_house_preferences(self):
        self.status = Status.WAIT_FOR_ME
        message = "Please tell your choice to proceed."
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_confirm_house_preferences(self):
        self.status = Status.WAIT_FOR_ME
        task = "The user is asked to confirm his preferences for apartment which he is going to rent. The user might want to make some changes if he is not satisfied with the preferences."
        options = [
            OptionsListType(id="1", title="✅ Yes"),
            OptionsListType(id="2", title="❌ No"),
        ]
        user_response = OptionParser.parse(
            user_task=task,
            options=options,
            user_input=self.current_input,
            openai_api_key=self.credentials["OPENAI_API_KEY"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
        )
        if user_response == "1":
            self.variables["validated_preferences"] = True
        elif user_response == "2":
            self.variables["validated_preferences"] = False
        else:
            self.variables["validated_preferences"] = None
        self.status = Status.MOVE_FORWARD

    def on_enter_confirm_house_preferences_again(self):
        self.standard_ask_again(
            message="Sorry I did not understand, please select a valid option."
        )

    def on_enter_ask_for_selecting_house_option(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(FSMOutput(message_data=MessageData(
            body="⏳ Please wait while we find the perfect house for you...")))

        out = template_property_details()
        self.send_message(
            FSMOutput(message_data=MessageData(
                body="Here are 3 options you might like:")
            )
        )

        self.variables['property_options'] = json.dumps(out["property_details"])
        for i, property in enumerate(out["property_details"]):
            message = (
                f"{property['property_id']} - {property['property_type']} in {property['locality']}, {property['city']}"
                f"\nRent: Rs. {property['monthly_rent']}/month"
                f"\nDeposit: Rs. {property['security_deposit']}"
                # f"\n\nTo choose this option type {i + 1}"
            )
            self.send_message(
                FSMOutput(message_data=MessageData(
                    header=property["property_id"],
                    body=message,
                    footer="Click below to book this property"),
                    type=MessageType.INTERACTIVE,
                    options_list=[
                        OptionsListType(id=str(i + 1), title="🔎 Inquiry")
                    ],
                )
            )
        self.status = Status.MOVE_FORWARD

    def on_enter_input_ask_for_selecting_house_option(self):
        self.status = Status.WAIT_FOR_ME
        services = [
            OptionsListType(id="4", title="❌ Cancel")
        ]
        message = "If you are interested in pursuing any of the options above, click on 🔎 Inquiry. \nElse click on 🔎 Show More below to see more houses"
        self.send_message(
            FSMOutput(
                message_data=MessageData(body=message),
                type=MessageType.INTERACTIVE,
                options_list=services,
            )
        )
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_ask_for_selecting_house_option(self):
        self.status = Status.WAIT_FOR_ME
        task = "The user is asked to choose any of the given 3 house properties or to show more properties or to cancel. The user might take sometime to choose an option."
        options = [
            OptionsListType(id="1", title="🔎 Inquiry"),
            OptionsListType(id="2", title="🔎 Inquiry"),
            OptionsListType(id="3", title="🔎 Inquiry"),
            OptionsListType(id="4", title="🔎 Show More"),
            OptionsListType(id="5", title="❌ Cancel")
        ]
        user_response = OptionParser.parse(
            user_task=task,
            options=options,
            user_input=self.current_input,
            openai_api_key=self.credentials["OPENAI_API_KEY"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
        )
        if user_response in ["1", "2", "3"]:
            property = json.loads(self.variables['property_options'])[int(self.current_input) - 1]
            self.variables["chosen_property"] = property
            self.variables["chosen_house_option"] = True
        else:
            self.variables["cancel_house_option"] = True
        self.status = Status.MOVE_FORWARD

    def on_enter_ask_for_confirming_property_visit(self):
        self.status = Status.WAIT_FOR_ME
        property = self.variables["chosen_property"]
        message = (
            "\nYour chosen property is:"
            f"\n\n{property['property_id']} - {property['property_type']} in {property['locality']}, {property['city']}"
            f"\nRent: Rs. {property['monthly_rent']}/month"
            f"\nDeposit: Rs. {property['security_deposit']}"
        )
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        monthly_rent = property["monthly_rent"]
        message = (
            "Before going for the property visit, make sure you have at least 10% of the rent amount.\n"
            f"\nThe rent for this property is Rs. {monthly_rent} per month."
            "\nPlease be ready to pay 10% of the amount to the landlord as an advance if you are interested in the property."
            "\nYou will have 48 hours to transfer the deposit and remaining rent amount."
            "\n\nAfter 48 hours, the property will be available to other tenants."
        )
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        services = [
            OptionsListType(id="1", title="✅ Confirm"),
            OptionsListType(id="2", title="❌ Not yet"),
        ]
        message = (
            "Please confirm that you have completed property visit to proceed."
        )
        self.send_message(
            FSMOutput(
                message_data=MessageData(body=message),
                type=MessageType.INTERACTIVE,
                options_list=services,
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_input_ask_for_confirming_property_visit(self):
        self.status = Status.WAIT_FOR_ME
        message = "Please tell your choice to proceed."
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_ask_for_confirming_property_visit(self):
        self.status = Status.WAIT_FOR_ME
        task = "The user is asked to confirm if he has completed the property visit. The user might take sometime to complete the visit."
        options = [
            OptionsListType(id="1", title="✅ Confirm"),
            OptionsListType(id="2", title="❌ Not yet"),
        ]
        user_response = OptionParser.parse(
            user_task=task,
            options=options,
            user_input=self.current_input,
            openai_api_key=self.credentials["OPENAI_API_KEY"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
        )
        if user_response == "1":
            self.variables["confirmed_property_visit"] = True
        elif user_response == "2":
            self.variables["confirmed_property_visit"] = False
        else:
            self.variables["confirmed_property_visit"] = None
        self.status = Status.MOVE_FORWARD

    def on_enter_ask_for_confirming_property_choice(self):
        self.status = Status.WAIT_FOR_ME
        services = [
            OptionsListType(id="1", title="⏱️ Need more time"),
            OptionsListType(id="2", title="❌ Cancel Booking"),
            OptionsListType(id="3", title="✅ Confirm Booking"),
        ]
        chosen_property = self.variables["chosen_property"]
        message = (
            f"Have you decided to proceed renting the property at"
            f"\n{chosen_property['property_id']}, {chosen_property['locality']}, {chosen_property['city']}"
        )
        self.send_message(
            FSMOutput(
                message_data=MessageData(body=message),
                type=MessageType.INTERACTIVE,
                options_list=services,
            )
        )
        self.status = Status.MOVE_FORWARD

    def on_enter_input_ask_for_confirming_property_choice(self):
        self.status = Status.WAIT_FOR_ME
        message = "Please tell your choice to proceed."
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.WAIT_FOR_USER_INPUT

    def on_enter_process_ask_for_confirming_property_choice(self):
        self.status = Status.WAIT_FOR_ME
        task = "The user is asked to confirm if he wants to rent the property. He can also cancel the booking if he is not satisfied with the property or he can ask for more time to think."
        options = [
            OptionsListType(id="1", title="⏱️ Need more time"),
            OptionsListType(id="2", title="❌ Cancel Booking"),
            OptionsListType(id="3", title="✅ Confirm Booking"),
        ]
        user_response = OptionParser.parse(
            user_task=task,
            options=options,
            user_input=self.current_input,
            openai_api_key=self.credentials["OPENAI_API_KEY"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
        )
        if user_response == "1":
            self.variables["property_visited"] = False
            self.variables["cancelled_booking"] = False
        elif user_response == "2":
            self.variables["property_visited"] = False
            self.variables["cancelled_booking"] = True
        elif user_response == "3":
            self.variables["cancelled_booking"] = False
            self.variables["property_visited"] = True
        self.status = Status.MOVE_FORWARD

    def on_enter_all_process_completed(self):
        self.status = Status.WAIT_FOR_ME
        chosen_property = self.variables["chosen_property"]
        day = self.variables["house_preferences"]["move_in_preference"].get("day")
        month = self.variables["house_preferences"]["move_in_preference"].get("month")
        message = (
            "👍👍 You are now ready to onboard the property."
            "\nProperty Address:"
            "\nhttps://maps.app.goo.gl/uNMhJZqHgZke3aaL7"
            f"\n\nYou can check in starting from {day} {month} 10am"
            "\nPlease provide this code at check-in:"
            f"\n{random.randint(10 ** 5, (10 ** 6) - 1)}"
            "\n\nYour stay details:"
            f"\n\n{chosen_property['property_id']} - {chosen_property['property_type']} in {chosen_property['locality']}, {chosen_property['city']}"
        )
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        message = (
            "👍👍 You are checked in!"
            "\nWe hope you are enjoying your stay!"
            "\nWe'll send you reminders when your monthly rent is due"
            "\nPay on time to become eligible for benefits like loans that can count towards your next rental !"
            "\nThank you for using the Housing App!"
        )
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def on_enter_booking_cancelled(self):
        self.status = Status.WAIT_FOR_ME
        message = "Your booking has been cancelled."
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def on_enter_cancel_house_option(self):
        self.status = Status.WAIT_FOR_ME
        message = "You have cancelled all house options. Thank you for using the Housing App"
        self.send_message(FSMOutput(message_data=MessageData(body=message)))
        self.status = Status.MOVE_FORWARD

    def is_valid_collected_preferences(self):
        if self.variables["validated_preferences"] is True:
            return True

    def is_invalid_collected_preferences(self):
        if self.variables["validated_preferences"] is False:
            return True

    def is_booking_confirm(self):
        if self.variables["property_visited"] is True:
            return True

    def is_needing_more_time(self):
        if self.variables["property_visited"] is False:
            return True

    def is_cancelled_booking(self):
        if self.variables["cancelled_booking"] is True:
            return True

    def is_cancelled_house_option(self):
        if self.variables["cancel_house_option"] is True:
            return True

    def is_chosen_house_option(self):
        if self.variables["chosen_house_option"] is True:
            return True

    def completed_property_visit(self):
        if self.variables["confirmed_property_visit"] is True:
            return True

    def not_yet_done_property_visit(self):
        if self.variables["confirmed_property_visit"] is False:
            return True

    def is_invalid_input_on_collected_preference(self):
        if self.variables["validated_preferences"] is None:
            return True

    def if_dialog_contains_selected_language(self):
        if self.current_input == "language_selected":
            return True
        return False

    def is_invalid_check_house_preferences(self):
        house_preferences = self.variables.get("house_preferences")
        if house_preferences.get("budget") and house_preferences.get("location"):
            return False
        return True

    def get_date_string(self, date_dict: dict):
        month_mapping = {
            "January": "01",
            "February": "02",
            "March": "03",
            "April": "04",
            "May": "05",
            "June": "06",
            "July": "07",
            "August": "08",
            "September": "09",
            "October": "10",
            "November": "11",
            "December": "12",
        }
        day = date_dict.get("day", "")
        month = date_dict.get("month", "")
        month_numeric = month_mapping.get(month, "")
        current_year = datetime.now().year
        formatted_date = f"{day}-{month_numeric}-{current_year}"
        return formatted_date

    def is_invalid_check_move_in_date(self):
        month_to_numeric_mapping = {
            "January": "1",
            "February": "2",
            "March": "3",
            "April": "4",
            "May": "5",
            "June": "6",
            "July": "7",
            "August": "8",
            "September": "9",
            "October": "10",
            "November": "11",
            "December": "12",
        }

        # mapping of numeric value to month name in string
        def is_date_in_future(day, month):
            # Check if both 'day' and 'month' are provided
            if day is not None and month is not None:
                # Get the current date
                current_date = datetime.now().date()
                target_date = datetime(current_date.year, int(month), int(day)).date()

                # Check if the target date is in the future
                return target_date > current_date
            # If either 'day' or 'month' is missing, return False
            return False

        date = self.variables["house_preferences"]["move_in_preference"]
        day = date.get("day")
        month = date.get("month")
        if day and month:
            month = month_to_numeric_mapping[date.get("month")]
            if is_date_in_future(day, month):
                return False
            else:
                return True
        else:
            return True

    def is_search_cancelled(self):
        return self.variables["cancelled_search"]


def test_machine(
    x: Type[AbstractFSM],
    send_message: callable,
    user_input: str = None,
    callback_input: str = None,
    credentials: Dict[str, Any] = None,
    **kwargs,
):
    """
    Method to test the FSM."""

    import json
    from pathlib import Path

    file = Path(x.__name__ + ".state")
    if file.exists():
        with open(file, "r") as f:
            state = json.load(f)
    else:
        state = None

    state = x.run_machine(
        send_message, user_input, callback_input, credentials, state, **kwargs
    )

    with open(file, "w") as f:
        json.dump(state, f, indent=4)


if __name__ == "__main__":
    import os

    os.remove("HousingAppFSM.state") if os.path.exists("HousingAppFSM.state") else None

    def cb(x: FSMOutput):
        print("\n\n")
        if x.message_data.header:
            print(x.message_data.header)
        if x.message_data.body:
            print(x.message_data.body)
        if x.message_data.footer:
            print(x.message_data.footer)
        if x.options_list:
            print(x.options_list)

    from collections import deque as Queue

    inputs = Queue(
        # [
        #     ("Hi", None),
        #     ("language_selected", None),
        #     ("I want a 3BHK in Mumbai with a budget of 30k", None),
        #     ("I want to move in on 15th March", None),
        # ]
    )
    credentials = {
        "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
        "AZURE_OPENAI_API_KEY": os.environ["AZURE_OPENAI_API_KEY"],
        "AZURE_OPENAI_API_VERSION": os.environ["AZURE_OPENAI_API_VERSION"],
        "AZURE_OPENAI_API_ENDPOINT": os.environ["AZURE_OPENAI_API_ENDPOINT"],
    }
    while True:
        user_input, callback_input = (
            inputs.popleft()
            if inputs
            else (
                input("Please provide input: "),
                input("Please provide callback input: "),
            )
        )
        print(f"User Input: {user_input}")
        print(f"Callback Input: {callback_input}")
        user_input = callback_input if not user_input else user_input
        test_machine(
            HousingAppFSM,
            cb,
            user_input,
            callback_input=callback_input,
            credentials=credentials,
        )
