# Alert Setup and Configuration

Alerts help you to stay posted when you're out and about. When a new slot is found the alerting backend will send
you a notification, so you can send it your confirmation SMS or book the appropriate appointment.  

Alerting backends are optional to configure. When a new slot is found the bot will alert you via Audio Text-to-Speech,
so if you're on your PC anyways while the bot is running, you're already set up.

Zulip is open source and can be hosted locally, since I use it mainly for various project automations it's what has the 
best documentation right now. Zulip also offers a public service, along with an app for every major smartphone OS.  

Messages older than 120 seconds will be ignored by the bot when waiting for interactive user input.  

Alerts can be tested using `python main.py --alerts` aka `python3 main.py --alerts`. 

## Currently supported alerting backends:

* Zulip
* Telegram
* Slack
* Pushover
* Gotify

## Zulip Setup

A full documentation of the backend can be found [here](https://chat.zulip.org/api/).

1. Register on https://chat.zulip.org/ and login
2. Open Settings

![Zulip Settings 1](/docs/zulip-1.jpg)

3. Navigate to Your bots. Choose `Generic bot` and enter Full name and Bot email to your choosing.

![Zulip Settings 2](/docs/zulip-2.jpg)

4. Note the displayed bot email and API key.

![Zulip Settings 3](/docs/zulip-3.jpg)

5. Next we'll have to get your user id rq. For that click on your username in the user-list and note the `user1234`-part.

![Zulip Settings 4](/docs/zulip-4.jpg)

6. Set the bot email and API key you noted in your `settings.py` as shown below. As `ZULIP_TARGET` use the user id we
   just got and add `<user-id>@chat.zulip.org`. Make sure you also set `ZULIP_ENABLED=True` and `ZULIP_TYPE='private'`.
   
```python
# Zulip (https://chat.zulip.org/api/)
ZULIP_ENABLED: bool = True
ZULIP_URL: str = 'https://chat.zulip.org/'
ZULIP_MAIL: str = 'impf-bot-bot@chat.zulip.org'
ZULIP_KEY: str = 'DSpu0w63ggjWV9AsQjeAWEzNyvW7qymq'
ZULIP_TYPE: str = 'private'  # private, stream
ZULIP_TARGET: str = 'user1234@chat.zulip.org'
ZULIP_TOPIC: str = 'General'
```

7. Download the Zulip smartphone app, login and test your bot using `python main.py --alerts` / `python3 main.py --alerts`. 
   If you should not get anynotification, check if your phone allows Zulip to send notifications and in-app if you 
   enabled notifications for private messages (`Settings` -> `Notifications` -> `Notifications when offline/online`)
   
![Zulip Settings 5](/docs/zulip-5.jpg)


## Telegram

⚠ Telegram Bots will only read the LATEST message in the chat (not older than 120 seconds)

1. Visit [BotFather](https://t.me/botfather) and send `/start`

2. Create a new bot by sending BotFather `/newbot` - choose the names freely

3. Send `/token` and obtain your `TELEGRAM_BOT_TOKEN` for `settings.py` or just copy it from the BotFather message after
   creating your bot. Start a chat with your bot and send it `/start`

4. To get your Chat ID send `/start` to [IDBot](https://t.me/myidbot) and then obtain your Chat ID using `/getid`.
   Set your ChatID at `TELEGRAM_BOT_CHATID` in `settings.py`
   
5. Start a private chat with your bot and send `/start`

## Slack

The remote booking feature is NOT (yet?) supported.

1. [Get a Slack Webhook URL](https://api.slack.com/messaging/webhooks)

2. Set the `SLACK_WEBHOOK_URL` in `settings.py` and set `SLACK_ENABLED` to `True`

## Gotify

Gotify offers a self hosted push-messaging server.

The remote booking feature is NOT supported since Gotify only works in the server -> client direction
