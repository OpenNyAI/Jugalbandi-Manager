---
layout: default
title: Telegram
---
## Telegram Integration with JB Manager

Telegram support is still under the development phase, but you can try it out using this guide.

### Steps to follow

a. **Create a JB Manager Bot**:
- Set up a bot with dummy WhatsApp credentials as described in the quickstart documentation.

b. **Create a Telegram Bot**:
- Use the *BotFather* chatbot on Telegram to create your bot.
- Acquire the token provided by *BotFather*. This token will be used to set up the webhook.

c. **Register the Telegram Channel**:
- To register the channel for your Telegram-based JB Manager bot, send a POST request to the localhost port 8000 (the API server running locally). Use the route `/v2/bot/<botID>/channel` with the following body:

  ```json
  {
    "name": "telegram",
    "type": "telegram",
    "url": "https://api.telegram.org/",
    "app_id": "<app_id>",
    "key": "<telegram token>",
    "status": "active"
  }
  ```
  `<botID>` and `<app_id>` can be extracted from the list of bots fetched using a GET request on `v1/bots` or `v2/`

d. **Set Up the Webhook**:
- Set the webhook by sending a POST request to `https://api.telegram.org/bot<token>/setWebhook` with the URL of the endpoint as the body under the `url` key. The format should be: `<tunnel_url>/v2/callback/telegram/<app_id>`.
- Example using `curl`:

  ```bash
  curl -X POST "https://api.telegram.org/bot<token>/setWebhook" -d "url=<tunnel_url>/v2/callback/telegram/<app_id>"
  ```

### Note: 

- **Dummy WhatsApp Credentials**: Ensure you have the necessary dummy credentials set up as per the initial bot creation instructions in Quickstart guide.
- **BotFather**: This is an official Telegram bot that helps you create and manage your Telegram bots. You can find it by searching for "BotFather" in the Telegram app.
- **Webhook URL**: The `<tunnel_url>` should be the URL where your API is hosted. Ensure it is accessible from the internet for Telegram to send updates to your bot.

   By following these steps, you can set up, integrate and test your Telegram-based JB Manager bot.

