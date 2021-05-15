import os
import re

import zulip

import settings
from impf.constructors import zulip_client, zulip_send_payload, zulip_read_payload

p = re.compile("^sms:\d{3}-?\d{3}$")

def sms_code(string: str) -> bool:
    return p.search(string.strip())

def read_code() -> str:
    """ Reads the alert code from any given platform and returns it as string """
    code = ''
    if settings.ZULIP_ENABLED:
        _code = zulip_read()
        if _code:
            print(f'Read SMS Code from Zulip: {_code}')
            code = _code

def send_alert(message: str) -> None:
    if settings.COMMAND_ENABLED:
        try: os.system(settings.COMMAND_LINE)
        except: pass
    if settings.ZULIP_ENABLED:
        zulip_send(message)

def zulip_send(message: str) -> None:
    client = zulip_client()
    request = zulip_send_payload()
    request.setdefault('content', message)
    r = client.send_message(request)
    if r.get('result') != 'success':
        print('Error sending Zulip message')

def zulip_read() -> str:
    client = zulip_client()
    request = zulip_read_payload()
    r = client.get_messages(request)

    for message in r.get('messages'):
        if sms_code(message.get('content')):
            return message.get('content').strip().replace('-')