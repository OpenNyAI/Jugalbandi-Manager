---
layout: default
title: Write Your Own Bot
---

Bots in JBManager follow a finite state machine paradigm.
Each Bot is represented by a python class which is a child class of `AbstractFSM` class present in jb-manager-bot module.

For this tutorial, we will be writing a very simple bot which asks user's name, age and gender and prints the captured information in the end.

Let us name our bot `UserFormBot`.

1. Create a class named `UserFormBot` which is a child class of `AbstractFSM`.
    ```python
    class UserFormBot(AbstractFSM):
        states = []
        transitions = []
        conditions = {}
        output_variables = set()

        def __init__(self, send_message: callable, credentials: Dict[str, Any] = None):
            if credentials is None:
                credentials = {}
            self.credentials = {}
            self.plugins: Dict[str, AbstractFSM] = {}
            super().__init__(send_message=send_message)
    ```

2. Each processing step which is performed by bot is represented by an state. Let's assume the bot will ask for preferred language in the first step and then greet the user in the second step. So, we need to define the appropriate states and transitions among states. Here, `zero` and `end` state represent starting and ending state of the bot, respectively. 
    ```python
    class UserFormBot(AbstractFSM):
        states = [
            "zero",
            "select_language",
            "welcome_message_display",
            "end"
        ]
        transitions = [
            {
                "source": "zero", 
                "dest": "select_language", 
                "trigger": "next"
            },
            {
                "source": "select_language",
                "dest": "welcome_message_display",
                "trigger": "next",
            },
            {
                "source": "welcome_message_display",
                "dest": "end",
                "trigger": "next",
            }
        ]
        conditions = {}
        output_variables = set()

        def __init__(self, send_message: callable, credentials: Dict[str, Any] = None):
            if credentials is None:
                credentials = {}
            self.credentials = {}
            self.plugins: Dict[str, AbstractFSM] = {}
            super().__init__(send_message=send_message)
    ```