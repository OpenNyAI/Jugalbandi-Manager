# Configuring the FSM to modify flows

As described previously, FSMs in Jugalbandi manager help define the conversation flow and manage state transitions. This component is vital in customising Jugalbandi for each use-case, and defines terms under which external plugins may be used, and controls the information to be fed into and interpreted from the LLMs. To achieve this, the FSM uses 3 concepts:&#x20;

* State: Represents a specific point in the conversation flow. (Eg: Initial state, greeting state, information retrieval state, end state etc.)\
  \
  Each state is typically associated with actions that the application is supposed to undertake, this can include asking the user questions, or processing the user-input or sending messages to a specified channel (such as whatsapp, telegram or any CMS or CRM system)\
  The ‘send\_message’ function allows the application to message the user within each state.\
  \
  A very simple FSM flow would include the following states:&#x20;
* Initial State: The bot waits for user input.(such as ‘Hi’)
* Greeting State: The bot greets the user.
* Info State: The bot provides the requested information.
* End State: The bot ends the conversation.

Global Variables: Global variables are defined in the FSM to cover core fields such as complainant name, address, dispute details, etc. These variables facilitate transitions between states.\
\
Status Indicators: Used to indicate the flow manager's actions:

* Wait for User Input
* Move Forward
* Wait for Callback (e.g., waiting for an API response in PULSE)
* Transition: The switch from one state to another.
* Condition: Determines whether a transition should occur, and specifies the logic to trigger said transition.&#x20;
* This refers to the prompts which give the LLMs context about their specific tasks in the application that’s utilising them.
* Lookup changes in the how-to guide of the indexer if any modifications are required in how the application would have to process the provided knowledge base.&#x20;

When configured properly, the FSM allows any developer to manage how their application interacts with users, in order to provide a structured and predictable user experience. Detailed explanations on how the FSMs can be built can be found in the how-to section of the technical documentation, along with a reference implementation of an FSM.&#x20;

\
