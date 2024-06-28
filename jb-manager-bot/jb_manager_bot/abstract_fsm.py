"""Module to define the abstract FSM class.
"""

from abc import ABC
from typing import Any, Dict, List, Set
from transitions import Machine

from jb_manager_bot.data_models import Status


class AbstractFSM(ABC):
    """Abstraction of the FSM class.
    Each use case will have its own FSM class.
    The FSM class will be used to define the states and transitions.
    """

    states: List[str] = []
    transitions: List[Dict[str, str]] = []
    conditions: Set[str] = set()
    output_variables: Set[str] = set()
    RUN_TOKEN = "RUNNING"

    def __init__(self, send_message: callable):
        """
        Initialize the FSM with a callback function.
        """
        self.send_message = send_message
        self.state = None
        self.status = Status.MOVE_FORWARD
        self.variables = {}
        self.outputs = {}
        self.plugins = self.plugins if hasattr(self, "plugins") else {}
        transitions = list(
            sorted(
                self.transitions,
                key=lambda x: (x.get("source"), x.get("conditions", "")),
                reverse=True,
            )
        )
        Machine(
            model=self,
            states=list(self.states),
            transitions=transitions,
            initial="zero",
        )

        self.__input__ = None
        self.__callback__ = None
        self.check_sanity()

    def initialise(self, **kwargs):
        """Method to initialise the FSM config."""
        for key, value in kwargs.items():
            self.variables[key] = value

    @property
    def current_input(self):
        """Property to get the current input."""
        return self.__input__

    @property
    def current_callback(self):
        """Property to get the current callback value."""
        return self.__callback__

    def run(self):
        """Method to start the FSM."""
        if self.status == Status.WAIT_FOR_PLUGIN:
            current_state = self.state
            state_method_name = f"on_enter_{current_state}"
            if hasattr(self, state_method_name):
                state_method = getattr(self, state_method_name)
                state_method()
        while self.status == Status.MOVE_FORWARD:
            self.next()
            self.reset_inputs()
        if self.status == Status.END:
            return self.outputs
        else:
            return self.RUN_TOKEN

    def submit_input(self, fsm_input: str):
        """Method to submit input to the FSM."""
        if fsm_input is not None:
            self.__input__ = fsm_input
            if self.status == Status.WAIT_FOR_USER_INPUT:
                self.status = Status.MOVE_FORWARD

    def submit_callback(self, fsm_callback: str):
        """Method to submit callback input to the FSM."""
        if fsm_callback is not None:
            self.__callback__ = fsm_callback
            if self.status == Status.WAIT_FOR_CALLBACK:
                self.status = Status.MOVE_FORWARD

    def reset_inputs(self):
        """Method to reset the inputs."""
        self.__input__ = None
        self.__callback__ = None

    def run_plugin(self, plugin: str, **kwargs):
        """Method to run a plugin."""
        plugin_obj: AbstractFSM = self.plugins.get(plugin)
        if not plugin_obj:
            raise ValueError(f"No such plugin found: {plugin}")
        if plugin_obj.state == "zero":
            plugin_obj.initialise(**kwargs)
        else:
            plugin_obj.submit_callback(self.current_callback)
            plugin_obj.submit_input(self.current_input)
        if (x := plugin_obj.run()) == plugin_obj.RUN_TOKEN:
            self.status = Status.WAIT_FOR_PLUGIN
            return self.RUN_TOKEN
        else:
            plugin_obj.reset()
            return x

    def _save_state(self):
        fsm_state = {
            "state": self.state,
            "status": self.status.value,
            "variables": self.variables,
        }
        plugin_states = {
            plugin: plugin_obj._save_state()
            for plugin, plugin_obj in self.plugins.items()
        }
        return {"main": fsm_state, "plugins": plugin_states}

    def _restore_state(self, state, status, variables, plugin_states):
        self.state = state
        self.status = Status(status)
        self.variables = variables
        for plugin, plugin_state in plugin_states.items():
            state = plugin_state["main"]["state"]
            status = Status(plugin_state["main"]["status"])
            variables = plugin_state["main"]["variables"]
            plugins = plugin_state["plugins"]
            self.plugins[plugin]._restore_state(state, status, variables, plugins)

    def reset(self):
        """Reset the FSM."""
        self.state = "zero"
        self.status = Status.MOVE_FORWARD
        self.variables = {}
        self.outputs = {}
        for plugin in self.plugins.values():
            plugin.reset()
        self.reset_inputs()

    def set_outputs(self):
        """Set the outputs of the FSM."""
        for key in self.output_variables:
            self.outputs[key] = self.variables.get(key, None)

    def on_enter_end(self):
        """Exit the FSM."""
        self.status = Status.WAIT_FOR_ME
        self.set_outputs()
        self.status = Status.END

    @classmethod
    def get_machine(
        cls,
        send_message: callable,
        credentials: Dict[str, Any] = None,
        state: str = None,
        status: Status = None,
        variables: Dict[str, Any] = None,
        plugin_states: Dict[str, Dict[str, Any]] = None,
    ):
        """Factory method to get FSM from state and variables."""
        if state is None:
            state = "zero"
        if variables is None:
            variables = {}
        if status is None:
            status = Status.MOVE_FORWARD
        if plugin_states is None:
            plugin_states = {}
        fsm = cls(send_message, credentials)
        fsm._restore_state(
            state=state, status=status, variables=variables, plugin_states=plugin_states
        )
        return fsm

    @classmethod
    def check_sanity(cls):
        """Check if the FSM is properly defined."""
        if len(cls.states) == 0:
            raise ValueError("No states defined")
        if len(cls.transitions) == 0:
            raise ValueError("No transitions defined")
        for condition in cls.conditions:
            if condition not in dir(cls):
                raise ValueError(f"Condition {condition} not defined in class {cls}")
        for state in cls.states:
            if not state == "zero" and f"on_enter_{state}" not in dir(cls):
                raise ValueError(
                    f"Implementation(On Enter Callback) of {state} not defined in class {cls}"
                )

    @classmethod
    def run_machine(
        cls,
        send_message: callable,
        user_input: str = None,
        callback_input: str = None,
        credentials: Dict[str, Any] = None,
        state: Dict[str, Any] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Method to run the FSM."""
        if state:
            fsm = cls.get_machine(
                send_message=send_message,
                credentials=credentials,
                state=state["main"]["state"],
                status=state["main"]["status"],
                variables=state["main"]["variables"],
                plugin_states=state["plugins"],
            )
        else:
            fsm = cls.get_machine(send_message=send_message, credentials=credentials)
        fsm.initialise(**kwargs)
        fsm.submit_callback(callback_input)
        fsm.submit_input(user_input)
        fsm.run()

        if fsm.status == Status.END:
            fsm.reset()

        return fsm._save_state()
