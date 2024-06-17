## Old Abstract FSM vs New Abstract FSM

1. Handling of Variables:
    - Old: Variables were stored in the `variables` attribute of the FSM. This was a dictionary with variable names as keys and their values as values. There were no type checks or type enforcement.
    - New:
      - Two types of variable: One Local which are temporary and acessed with in the state and other Global which are shared across states. Example: `error_code` is a local variable used in the plugin calls.
        - Local (Temporary) Variables are stored in the `temp_variables` attribute of the AbstractFSM. This is a dictionary with variable names as keys and their values as values. The `self.temp_variables` is already set in the constructor of the AbstractFSM.
        - Global Variables need to be initialized inside a pydantic class, inheriting from `pydantic.BaseModel`. This allows for type checking and type enforcement. When inheriting AbstractFSM to create a Bot Class, set `variable_names = Your_Pydantic_Variables_Class` as class variable to enforce type checking and type enforcement. And later in the constructor of the Bot Class, initialize self.variables = Your_Pydantic_Variables_Class() to initialize the variables. Example: `self.variables = Your_Pydantic_Variables_Class()`
2. Use of Helper Functions:
    - Old: Earlier all the on_enter, is_valid and other functions needed to be defined in the FSM class itself.
    - New: We use helper function for each type of state, which are pre-defined in the AbstractClass. For example, if creating a on_enter for a display state, we can use `self._on_enter_display` function.
    1. `display` state: `_on_enter_display`
      1. Params: 
          1. message,
          2. options: list of button options,
          3. dialog: if the list of options greater than 3, then dialog will be displayed.
          4. menu_selector: description of the menu.,
          5. menu_title: title of the menu.,
          6. media_url: if the message is a media file, then the url of the media file.,
          7. dest_channel: default "out",
    2.  `input` state: `_on_enter_input`
      1.  No params
    3. `input logic` state: `_on_enter_input_logic` (Handles the LLM Call for parsing user input into required format)
      1. Params:
          1.  write_var: variable name as mentioned in the Pydantic Variable Class
          2.  options: list of options for the user to select from 
          3.  message: message shown to the user asking for input
          4.  validation: validation str as python expression
   1. `assignment` state: `_on_enter_assign` (Handles logic for variable manipulation)
      1. Params:
         1. variable_name: variable name as mentioned in the Pydantic Variable Class
         2. validation: should be a lambda function
   2. `branching` state: `_on_enter_empty_branching` (Empty Function)
      1. No params
   3. `plugin` state: `_on_enter_plugin` (Handles the plugin call)
      1. You should import your plugin as a function.
      2. Params:
         1. plugin: plugin function
         2. input_variables: dict mapping of the parameters to the plugin and corresponing variables in the fsm.
         3. output_variables: dict mapping of the output variables from the plugin to the fsm variables.
         4. message: if any message to be displayed to the user.
   4. plugin error code validation: `_on_enter_plugin_error_code_validation` (Handles the error code validation)
      1. Params:
         1. error_code: value of the error code
   5. other validation function for conditional transition: `_validate_method` (Handles the validation of the condition)
      1. Params:
         1. validation: should be a lambda function
         2. variable_name: variable name as mentioned in the Pydantic Variable Class
         
        