import os
import unittest
from jb_manager_bot.parsers.option_parser import OptionParser, Parser
from jb_manager_bot.data_models import OptionsListType


class TestOptionParser(unittest.TestCase):

    def setUp(self):
        # Load credentials from environment variables
        self.credentials = {
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
            "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
            "AZURE_OPENAI_API_ENDPOINT": os.getenv("AZURE_OPENAI_API_ENDPOINT"),
            "FAST_MODEL": os.getenv("FAST_MODEL"),
        }

    def test_option_parser(self):
        user_input = "I want to buy a car."
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
            user_input,
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            model=self.credentials["FAST_MODEL"],
        )

        expected_result = "1"
        self.assertEqual(result, expected_result)

    def test_parser_with_options(self):
        user_input = "9 am around"
        expected_result = "1"
        validation = None

        message = (
            "Please enter the time of day you would like to schedule your appointment (Morning, Afternoon, Evening):",
        )
        task = f"This is the question being asked to the user: {message}. This is validation that the variable need to pass {validation}. Format and modify the user input into the format requied and if you could not be decide return None. Based on the user's input, return the output in json format: {{'result': <input>}}"

        options = [
            OptionsListType(id="1", title="Morning"),
            OptionsListType(id="2", title="Afternoon"),
            OptionsListType(id="3", title="Evening"),
        ]        
        result = Parser.parse_user_input(

            user_task=task,
            options=options,
            user_input= user_input,
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
        )
        result = result["id"]
        self.assertEqual(result, expected_result)
    
    def test_parser_wo_options(self):
        message="Please enter the date you would like to schedule your appointment (YYYY-MM-DD):"
        validation = "re.match(r'^\d{4}-\d{2}-\d{2}$', appointment_date) is not None"
        task = f"This is the question being asked to the user: {message}. This is validation that the variable need to pass {validation}. Format and modify the user input into the format requied and if you could not be decide return None. Based on the user's input, return the output in json format: {{'result': <input>}}"
        user_input = "26th December 2019"
        expected_result = "2019-12-26"
        result = Parser.parse_user_input(
            user_task=task,
            options=None,
            user_input=user_input,
            azure_endpoint=self.credentials["AZURE_OPENAI_API_ENDPOINT"],
            azure_openai_api_key=self.credentials["AZURE_OPENAI_API_KEY"],
            azure_openai_api_version=self.credentials["AZURE_OPENAI_API_VERSION"],
        )
        result = result["result"]
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
