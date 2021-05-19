import os
import re
import logging
from typing import Union

import settings
from impf.constructors import zulip_client, zulip_send_payload, zulip_read_payload, get_command

import requests

HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'https://github.com/alfonsrv/impf-botpy'
}

logger = logging.getLogger(__name__)
p = re.compile(r"sms:\d{3}-?\d{3}")

if settings.TELEGRAM_ENABLED:
    import telebot
    import json
    bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Impf-Bot successfully connected. Scanning for Appointments now.")
        data = {}
        # store chatId for later to send alerts
        data["message_id"] = message.from_user.id
        data["offset"] = 0
        json.dump(data, open('telegram.json', 'w'))
        bot.stop_polling()

    try:
        f=open('telegram.json', 'r')
    except IOError:
        logger.warning(f"Send the message '/start' to your telegram bot!")
        # start polling until reception of /start.
        bot.polling()


def sms_code(string: str) -> Union[str, None]:
    """ Checks if string contains a valid SMS code """
    m = p.search(string.strip())
    if m: m = m.group().replace('-', '').replace('sms:', '')
    return m


def read_code() -> str:
    """ Reads the alert code from any given platform and returns it as string """
    code = ''
    if settings.ZULIP_ENABLED:
        _code = zulip_read()
        if _code:
            logger.info(f'Read SMS Code from Zulip: {_code}')
            code = _code
    if settings.TELEGRAM_ENABLED:
        _code = telegram_read()
        if _code:
            logger.info(f'Read SMS Code from Telegram: {_code}')
            code = _code

    return code


def send_alert(message: str) -> None:
    logger.info(f'Sending alert "{message}"')
    if settings.COMMAND_ENABLED:
        try: os.system(get_command())
        except: pass
    if settings.ZULIP_ENABLED:
        zulip_send(message)
    if settings.TELEGRAM_ENABLED:
        telegram_send(message)
    if settings.PUSHOVER_ENABLED:
        pushover_send(message)


def zulip_send(message: str) -> None:
    client = zulip_client()
    if client is None: return
    request = zulip_send_payload()
    request.setdefault('content', message)
    r = client.send_message(request)
    if r.get('result') != 'success':
        logger.error(f'Error sending Zulip message - got {r}')


def zulip_read() -> str:
    client = zulip_client()
    if client is None: return
    request = zulip_read_payload()
    r = client.get_messages(request)

    for message in r.get('messages'):
        if sms_code(message.get('content')):
            return sms_code(message.get('content'))


def telegram_send(message: str) -> None:
    data = json.load(open('telegram.json', 'r'))
    bot.send_message(data["message_id"],message)
        
def telegram_read() -> str:
    data = json.load(open('telegram.json', 'r'))
    msgs = bot.get_updates(data["offset"])
    for msg in msgs:
        if msg.message is not None:
            # store offset of the update to a file to ignore the message in the future
            data["offset"]=msg.update_id+1
            json.dump(data, open('telegram.json', 'w'))
            if sms_code(msg.message.text.lower()):
                return sms_code(msg.message.text.lower())

def pushover_send(message: str) -> None:
    app_token = settings.PUSHOVER_APP_TOKEN
    user_key = settings.PUSHOVER_USER_KEY

    url = f'https://api.pushover.net/1/messages.json'
    data = {
        'token': app_token,
        'user': user_key,
        'message': message
    }

    response = requests.post(url, data=data)
    logger.debug(response)