---
layout: default
title: Write Your Own Bot
---

Bots in JBManager follow a finite state machine paradigm, using the `transitions` library. It is recommended to refer [transitions documentation](https://github.com/pytransitions/transitions?tab=readme-ov-file#quickstart) to understand the basic concepts of states, transitions & conditions.

Each Bot is represented by a python class which is a child class of `AbstractFSM` class present in jb-manager-bot module.

```python
class BotCode(AbstractFSM):
    states = []
    transitions = []
    conditions = {}
    output_variables = set()

    def __init__(self, send_message: callable, credentials: Dict[str, Any] = None):
        if credentials is None:
            credentials = {}
        self.credentials = {}
        super().__init__(send_message=send_message)
```
`credentials` in constructor contains all the credentials that will be required by the bot. You can define these credentials while installing the bot in JBManager UI. Values of credentials are passed while configuring the bot in JBManager UI. These credentials are passed in the `credentials` dict in the constructor, with credential name as key and credential secret as value. Save this credential as an instance variable `credentials`, after performing sanity check if the credentials are present.

A new instance of Bot is initialised for each user session, maintaining seperation between user session.

## States 
Each processing step in the Bot flow is represented be a state. This is same as state defined in the transitions library.

**Declaration:** To declare state in Bot code in JBManager, add the state name in states list class variable of your bot code.

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "new_state_name",
        ...
    ]
```

**Definition:** To define the state, create a instance method of name `on_enter_<state_name>` in your Bot class. 

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "new_state_name",
        ...
    ]

    def on_enter_new_state_name(self):
        self.status = Status.WAIT_FOR_ME
        ...
        # State processing logic
        ...
        self.status = Status.MOVE_FORWARD
```
## Status
Each bot running on JBManager can have 4 different status which controls the flow of the bot. The various status are described below:
1. `WAIT_FOR_ME` -  It should be used on the top of each state definition representing processing logic of a state is currently executing and should wait for processing to finish before making transition to any other state.
2. `MOVE_FORWARD` - It represents that current processing is finished and the FSM is ready to transition to next state.
3. `WAIT_FOR_USER_INPUT` - It represents that FSM should wait for user input before making transition to another state. It is used in cases where the FSM wants to capture the user input. The next state after this state should contain the logic to handle the user input.
4. `WAIT_FOR_CALLBACK` - It represents that FSM should wait for external before making transition to another state. It is used in cases where the FSM wants to capture the input from 3rd party webhook APIs. The next state after this state should contain the logic to handle the callback input.
5. `WAIT_FOR_PLUGIN` - For internal use only.
6. `END` - It represents the end of the bot flow. It should be added at the last state of the bot flow.

**NOTE:** `WAIT_FOR_ME` should only be used at start of the state definition. `MOVE_FORWARD`, `WAIT_FOR_USER_INPUT`, `WAIT_FOR_CALLBACK` and `END` should be used at the end of state definition. `WaIT_FOR_PLUGIN` should never be used in any custom FSM. 

## Transitions
The switch from one state to another state is managed by defining `transition` in Bot class. After completing the current state, the bot will switch to the state as defined by the transition. 

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "first_state",
        "second_state"
        ...
    ]
    transitions = [
        ...
        {
            "source": "first_state",  # Source State
            "dest": "second_state",  # Destination State
            "trigger": "next"   # Trigger, value will always be next for JBManager
        }
        ...
    ]
```
In the above example, after completing the `first_state`, the bot will switch to executing `second_state`.
In case the bot is defined to wait for user input or webhook callback after first state (by setting appropriate status in the end), the bot will wait after executing `first_state` and only after recieving user input or webhook callback(whichever applicable), it will switch to `second_state`.

### Conditional Transition
If the next state to switch depends on a boolean condition, conditional transition can be defined to switch. We need define the transition with `conditions` key and appropriate condition should also be declared and defined.

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "first_state",
        "second_a_state",
        "second_b_state",
        ...
    ]
    transitions = [
        ...
        {
            "source": "first_state",
            "dest": "second_a_state",
            "trigger": "next",
            "conditions": "is_second_a",   # using condition a
        },
        {
            "source": "first_state",
            "dest": "second_b_state",
            "trigger": "next",
            "conditions": "is_second_b",   # using condition b
        },
        ...
    ]
    conditions = {
        "is_second_a",  # Declaring condition a
        "is_second_b"   # Declaring condition b
    }
```

To define the condition, create an instance method with the same name as condition name. The method should return boolean `True` value denoting the condition to be satisfied, else `False` denoting the condition is not satisfied.

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "first_state",
        "second_a_state",
        "second_b_state",
        ...
    ]
    transitions = [
        ...
        {
            "source": "first_state",
            "dest": "second_a_state",
            "trigger": "next",
            "conditions": "is_second_a",   # using condition a
        },
        {
            "source": "first_state",
            "dest": "second_b_state",
            "trigger": "next",
            "conditions": "is_second_b",   # using condition b
        },
        ...
    ]
    conditions = {
        "is_second_a",  # Declaring condition a
        "is_second_b"   # Declaring condition b
    }
    
    ...

    def is_second_a(self):
        ...
        # condition a logic here
        ...
        return is_condition_a_satisifed
    
    def is_second_b(self):
        ...
        # condition b logic here
        ...
        return is_condition_b_satisifed
```
In the above example, after finishing the `first_state`, bot will call the conditions associated with `first_state` as source. Whichever condition returns `True`, bot will take that transition and switch to appropriate state defined in the `dest` of the transition. If multiple conditions are satisfied, bot will take the transition which is defined first in the `transitions` list. 
For more details on the working of transitions, see [transitions documentation](https://github.com/pytransitions/transitions).

## Variables
To retain information across the states, use `variables` dictionary defined in the `AbstractFSM`, with variable name as key in string format and value for the variable data. 

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "new_state_name",
        ...
    ]

    def on_enter_new_state_name(self):
        self.status = Status.WAIT_FOR_ME
        ...
        # State processing logic
        
        self.variables["my_variable"] = 10 # Here we are setting my_variable value to 10
        your_variable = self.variables("your_variable") # Here we are accessing your_variable set in any previous state
        
        # State processing logic
        ...
        self.status = Status.MOVE_FORWARD
```
**NOTE:** Add only json serializable keys and values to the `variables` dictionary.

## User Input
To access input by user inside a state, use the instance variable `current_input` defined in the `AbstractFSM` class. This variable contains the value of current user input in `str` data type format.

**Note:** Variable `current_input` will contain the value of user input within the scope of state which comes next to input state i.e state ends with `WAIT_FOR_USER_INPUT` status. It contains `None` in any other state. 

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "user_input_processing_state",
        ...
    ]

    def on_enter_user_input_processing_state(self):
        self.status = Status.WAIT_FOR_ME
        ...
        user_input = self.current_input
        # user input processing logic
        ...
        self.status = Status.MOVE_FORWARD
```

## Webhook Input
To access input by an 3rd party webhook api inside a state, use the instance variable `current_callback` defined in the `AbstractFSM` class. This variable contains the value of current webhook data in `str` data type format (You might need to parse it to json).

**Note:** Variable `current_callback` will contain the value of webhook data within the scope of state which comes next to callback state i.e state ends with `WAIT_FOR_CALLBACK` status. It contains `None` in any other state. 

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "webhook_processing_state",
        ...
    ]

    def on_enter_webhook_processing_state(self):
        self.status = Status.WAIT_FOR_ME
        ...
        webhook_data = self.current_callback
        webhook_data = json.loads(webhook_data)
        # webhook processing logic
        ...
        self.status = Status.MOVE_FORWARD
```

## Sending Message to User
To send a message back to user from the bot, use `send_message` method defined in the `AbstractFSM` class. `send_message` method takes `FSMOutput` object as an arguement. Populate the object of `FSMOutput` class according to the message you want to send to user.

```python
class BotCode(AbstractFSM):
    states = [
        ...
        "greet_user",
        ...
    ]

    def on_enter_greet_user(self):
        self.status = Status.WAIT_FOR_ME
        self.send_message(
            FSMOutput(
                message_data=MessageData(
                    body="Hello! How are you?" # Message Text
                ),
                type=MessageType.TEXT, # Text Message
                dest="out", # Destination of the message
            )
        )
        self.status = Status.MOVE_FORWARD
```

For more details, see FSMOutput documentation.
#### Possible destinations
1. `out` - The message will follow translation(if applicable) and converted to speech and sent it to user.
2. `channel` - There are some messages which don't require translation and should be interpreted as a special message. Those could be either flags for language selection or metadata for the forms which will be displayed to user.
3. `rag` - The message will go to RAG component of JBManager instead of user.  
