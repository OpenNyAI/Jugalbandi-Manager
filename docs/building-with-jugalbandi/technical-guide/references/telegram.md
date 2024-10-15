---
layout: default
title: Telegram
---
## Telegram Integration with JB Manager

### Steps to follow

a. **Create a Telegram Bot**:

- Use the *BotFather* chatbot on Telegram to create your bot
- Acquire the token provided by *BotFather*. This token will be used to set up the webhook

b. **Create a JB Manager Bot**:

- Set up a bot as described in the quickstart documentation
- Select type as `telegram` and appropriate details while creating the channel

c. **Set-up the Webhook**:

- Set the webhook by sending a POST request to `https://api.telegram.org/bot<token>/setWebhook` with the URL of the endpoint as the body under the `url` key. The format should be: `<tunnel_url>/v2/callback/telegram/<app_id>`.
- Example using `curl`:

  ```bash
  curl -X POST "https://api.telegram.org/bot<token>/setWebhook" -d "url=<tunnel_url>/v2/callback/telegram/<app_id>"
  ```

### Note:

- **BotFather**: This is an official Telegram bot that helps you create and manage your Telegram bots. You can find it by searching for "BotFather" in the Telegram app
- **Webhook URL**: The `<tunnel_url>` should be the URL where your API is hosted. Ensure it is accessible from the internet for Telegram to send updates to your bot

  By following these steps, you can set up, integrate and test your Telegram-based JB Manager bot.
