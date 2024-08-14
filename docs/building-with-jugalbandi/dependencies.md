# Dependencies

While each use case will have different dependencies based on the services they choose to provide,and the medium through which Jugalbandi has to operate, some of the dependencies that are common across all implementations are:&#x20;

1. Kafka: Manages message exchange between different parts of the system for real-time data flow.
2. Postgres Database: Stores user data and conversation history for reliable data access.
3. Bhashini Service: Handles language translation to support multilingual interactions. Or,\
   Azure Speech: Converts spoken words to text and text to spoken words for voice interactions.
4. Whatsapp/Telegram API or API management services: Ensure the API host is correctly set up and accessible.
