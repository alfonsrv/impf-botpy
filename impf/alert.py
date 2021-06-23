import os
import re
import logging
from time import time
from typing import Union, Callable

import settings
from impf.constructors import zulip_client, zulip_send_payload, zulip_read_payload, get_command

import requests

from impf.decorators import alert_resilience
from impf.exceptions import AlertError

HEADERS = {
    'Accept': 'application/json',
    'User-Agent': 'https://github.com/alfonsrv/impf-botpy'
}

logger = logging.getLogger(__name__)
SMS_RE = re.compile(r"sms:\d{3}-?\d{3}")
APPT_RE = re.compile(r"appt:\d")


def sms_code(string: str) -> Union[str, None]:
    """ Checks if string contains a valid SMS code """
    if not string: return ''
    m = SMS_RE.search(string.strip())
    if m: m = m.group().replace('-', '').replace('sms:', '')
    return m


def appointment_slot(string: str) -> Union[str, None]:
    """ Checks if string contains a valid appointment wish """
    if not string: return ''
    m = APPT_RE.search(string.strip())
    if m: m = m.group().replace('appt:', '')
    return m


def _read_backend(backend_func: Callable, match_func: Callable) -> str:
    """ Helper function to abstract backend reads """
    code = backend_func(match_func)
    if code:
        logger.info(f'Read {match_func.__name__.upper()} Code from '
                    f'{backend_func.__name__.replace("_read", "").capitalize()}: {code}')
    return code


def read_backend(case: str) -> str:
    """ Reads the SMS Code from any of the confired alerting backends and returns it as string """
    match_func = sms_code if case == 'sms' else appointment_slot
    code = ''
    if settings.ZULIP_ENABLED:
        code = _read_backend(zulip_read, match_func) or code
    if settings.TELEGRAM_ENABLED:
        code = _read_backend(telegram_read, match_func) or code
    return code


def send_alert(message: str) -> None:
    logger.info(f'Sending alert "{message}"')
    if settings.COMMAND_ENABLED:
        execute_command()
    if settings.ZULIP_ENABLED:
        zulip_send(message)
    if settings.TELEGRAM_ENABLED:
        telegram_send(message)
    if settings.SLACK_ENABLED:
        slack_send(message)
    if settings.PUSHOVER_ENABLED:
        pushover_send(message)
    if settings.GOTIFY_ENABLED:
        gotify_send(message)


@alert_resilience
def execute_command() -> None:
    os.system(get_command())


@alert_resilience
def zulip_send(message: str) -> None:
    """ Just send a message; no logic going on here """
    client = zulip_client()
    if client is None: return
    request = zulip_send_payload()
    request.setdefault('content', message)
    r = client.send_message(request)
    if r.get('result') != 'success': raise AlertError(r.get('code'), r.get('msg'))


@alert_resilience
def zulip_read(match_func: Callable) -> Union[None, str]:
    client = zulip_client()
    if client is None: return
    request = zulip_read_payload()
    r = client.get_messages(request)
    if r.get('result') != 'success': raise AlertError(301, r)
    for message in r.get('messages'):
        # wenn im erwarteten Format und innerhalb der letzten 2 Minuten
        if match_func(message.get('content')) and time() - message.get('timestamp') <= 120:
            return match_func(message.get('content'))

@alert_resilience
def slack_send(message: str) -> None:
    url = settings.SLACK_WEBHOOK_URL
    payload = {
        'text': message,
        'username': 'Impf-Bot.py'
    }

    r = requests.post(url, json=payload, headers=HEADERS)
    if r.status_code != 200: raise AlertError(r.status_code, r.text)
    logger.debug(r)

@alert_resilience
def telegram_send(message: str) -> None:
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_API_TOKEN}/sendMessage'
    params = {
        'chat_id': settings.TELEGRAM_CHAT_ID,
        'parse_mode': 'Markdown',
        'text': message
    }

    r = requests.get(url, params=params, headers=HEADERS)
    if r.status_code != 200: raise AlertError(r.status_code, r.text)
    logger.debug(r)


@alert_resilience
def telegram_read(match_func: Callable) -> Union[None, str]:
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_API_TOKEN}/getUpdates'
    params = {
        'chat_id': settings.TELEGRAM_CHAT_ID,
        'offset': -1
    }

    r = requests.get(url, params=params, headers=HEADERS)
    logger.debug(r)
    if r.status_code != 200: raise AlertError(r.status_code, r.text)
    for message in r.json().get('result'):
        _message = message.get('message')
        if not _message: return
        # wenn im erwarteten Format und innerhalb der letzten 2 Minuten
        if match_func(_message.get('text')) and time() - _message.get('date') <= 120:
            return match_func(_message.get('text'))


@alert_resilience
def pushover_send(message: str) -> None:
    url = f'https://api.pushover.net/1/messages.json'
    data = {
        'token': settings.PUSHOVER_APP_TOKEN,
        'user': settings.PUSHOVER_USER_KEY,
        'title': 'Impf-Bot.py Notification',
        'sound': 'persistent',
        'priority': 1,
        'message': message
    }

    r = requests.post(url, data=data)
    if r.status_code != 200: raise AlertError(r.status_code, r.text)
    logger.debug(r)

@alert_resilience
def gotify_send(message: str) -> None:
    url = f'{settings.GOTIFY_URL}/message'
    params = (
        ('token', f'{settings.GOTIFY_APP_TOKEN}'),
    )
    files = {
        'title': (None, 'impf-botpy'),
        'message': (None, f'{message}'),
        'priority': (None, '5'),
    }
    r = requests.post(url, params=params, files=files)
    if r.status_code != 200: raise AlertError(r.status_code, r.text)
    logger.debug(r)
