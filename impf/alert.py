import os
import re
import logging
from time import time
from typing import Union, Callable

import settings
from impf.constructors import zulip_client, zulip_send_payload, zulip_read_payload, get_command

import requests

HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'https://github.com/alfonsrv/impf-botpy'
}

logger = logging.getLogger(__name__)
SMS_RE = re.compile(r"sms:\d{3}-?\d{3}")
APPT_RE = re.compile(r"appt:\d")


# TODO: Make the following 3 functions pythonic
def sms_code(string: str) -> Union[str, None]:
    """ Checks if string contains a valid SMS code """
    m = SMS_RE.search(string.strip())
    if m: m = m.group().replace('-', '').replace('sms:', '')
    return m


def appointment_slot(string: str) -> Union[str, None]:
    """ Checks if string contains a valid appointment wish """
    m = APPT_RE.search(string.strip())
    if m: m = m.group().replace('appt:', '')
    return m


def read_backend(case: str) -> str:
    """ Reads the SMS Code from any of the confired alerting backends and returns it as string """
    match_func = sms_code if case == 'sms' else appointment_slot
    code = ''
    if settings.ZULIP_ENABLED:
        _code = zulip_read(match_func)
        if _code:
            logger.info(f'Read {case.capitalize()} Code from Zulip: {_code}')
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
    """ Just send a message; no logic going on here """
    client = zulip_client()
    if client is None: return
    request = zulip_send_payload()
    request.setdefault('content', message)
    r = client.send_message(request)
    if r.get('result') != 'success':
        logger.error(f'Error sending Zulip message - got {r}')


def zulip_read(match_func: Callable) -> str:
    client = zulip_client()
    if client is None: return
    request = zulip_read_payload()
    r = client.get_messages(request)
    for message in r.get('messages'):
        # wenn im erwarteten Format und innerhalb der letzten 2 Minuten
        if match_func(message.get('content')) and time() - message.get('timestamp') <= 120:
            return match_func(message.get('content'))


def telegram_send(message: str) -> None:
    api_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_BOT_CHATID

    url = f'https://api.telegram.org/bot{api_token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'text': message
    }

    response = requests.get(url, params=params, headers=HEADERS)
    logger.debug(response)


def pushover_send(message: str) -> None:
    url = f'https://api.pushover.net/1/messages.json'
    data = {
        'token': settings.PUSHOVER_APP_TOKEN,
        'user': settings.PUSHOVER_USER_KEY,
        'message': message
    }

    response = requests.post(url, data=data)
    logger.debug(response)