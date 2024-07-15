import unittest
import os
from neocarwash import NeoCarWashFSM
from jb_manager_bot import AbstractFSM, FSMOutput
from typing import Type, Dict, Any
from collections import deque as Queue


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
    if x.media_url:
        print(x.media_url)


inputs = Queue(
    [
        ("start", None),
        ("eng", None),
        ("buy", None),
        ("20 december 2024", None),
        ("9 am", None),
        ("no", None),
        # ("2022-12-12", None),
        # ("morning", None),
        # ("no", None),
    ]
)
expected_states = Queue(
    [
        {
            "main": {
                "state": "language_selection",
                "status": 1,
                "variables": {
                    "selected_service": None,
                    "appointment_date": None,
                    "appointment_time": None,
                    "availability_status": None,
                    "booking_message": None,
                    "further_assistance": None,
                    "booking_status": None,
                    "appointment_image": None,
                    "error_code": None,
                    "fail_service_count": 0,
                },
            },
            "plugins": {},
        },
        {
            "main": {
                "state": "service_selection_input",
                "status": 1,
                "variables": {
                    "selected_service": None,
                    "appointment_date": None,
                    "appointment_time": None,
                    "availability_status": None,
                    "booking_message": None,
                    "further_assistance": None,
                    "booking_status": None,
                    "appointment_image": None,
                    "error_code": None,
                    "fail_service_count": 0,
                },
            },
            "plugins": {},
        },
        {
            "main": {
                "state": "date_input",
                "status": 1,
                "variables": {
                    "selected_service": "Buy a Car",
                    "appointment_date": None,
                    "appointment_time": None,
                    "availability_status": None,
                    "booking_message": None,
                    "further_assistance": None,
                    "booking_status": None,
                    "appointment_image": None,
                    "error_code": None,
                    "fail_service_count": 0,
                },
            },
            "plugins": {},
        },
        {
            "main": {
                "state": "time_input",
                "status": 1,
                "variables": {
                    "selected_service": "Buy a Car",
                    "appointment_date": "2024-12-20",
                    "appointment_time": None,
                    "availability_status": None,
                    "booking_message": None,
                    "further_assistance": None,
                    "booking_status": None,
                    "appointment_image": None,
                    "error_code": None,
                    "fail_service_count": 0,
                },
            },
            "plugins": {},
        },
        {
            "main": {
                "state": "further_assistance_input",
                "status": 1,
                "variables": {
                    "selected_service": "Buy a Car",
                    "appointment_date": "2024-12-20",
                    "appointment_time": "Morning",
                    "availability_status": None,
                    "booking_message": None,
                    "further_assistance": None,
                    "booking_status": "confirmed",
                    "appointment_image": "https://d27jswm5an3efw.cloudfront.net/app/uploads/2019/08/image-url-3.jpg",
                    "error_code": None,
                    "fail_service_count": 0,
                },
            },
            "plugins": {},
        },
        {
            "main": {
                "state": "zero",
                "status": 2,
                "variables": {
                    "selected_service": None,
                    "appointment_date": None,
                    "appointment_time": None,
                    "availability_status": None,
                    "booking_message": None,
                    "further_assistance": None,
                    "booking_status": None,
                    "appointment_image": None,
                    "error_code": None,
                    "fail_service_count": 0,
                },
            },
            "plugins": {},
        },
    ]
)


class TestAbstractFSM(unittest.TestCase):
    def setUp(self) -> None:
        self.credentials = {
            "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
            "AZURE_OPENAI_API_KEY": os.environ["AZURE_OPENAI_API_KEY"],
            "AZURE_OPENAI_API_VERSION": os.environ["AZURE_OPENAI_API_VERSION"],
            "AZURE_OPENAI_API_ENDPOINT": os.environ["AZURE_OPENAI_API_ENDPOINT"],
            "FAST_MODEL": os.environ["FAST_MODEL"],
            "SLOW_MODEL": os.environ["SLOW_MODEL"],
        }

    def test_abstract_fsm(self):
        state = None
        while inputs:
            user_input, callback_input = inputs.popleft()
            excepted_state = expected_states.popleft()
            user_input = callback_input if not user_input else user_input

            state = NeoCarWashFSM.run_machine(
                cb, user_input, callback_input, self.credentials, state
            )
            self.assertEqual(state, excepted_state)


if __name__ == "__main__":
    unittest.main()
