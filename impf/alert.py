import os
import re
import logging
from typing import Union

import settings
from impf.constructors import zulip_client, zulip_send_payload, zulip_read_payload, get_command

import requests

logger = logging.getLogger(__name__)
p = re.compile("sms:\d{3}-?\d{3}")


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
    bot_token = settings.TELEGRAM_BOT_TOKEN
    bot_chatID = settings.TELEGRAM_BOT_CHATID

    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + message

    response = requests.get(send_text)