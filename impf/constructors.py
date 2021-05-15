import zulip

import settings

def zulip_send_payload() -> dict:
    request = {
        'type': settings.ZULIP_TYPE,
        'to': settings.ZULIP_TARGET,
    }
    if request.get('type') == 'stream': request.setdefault('topic', settings.ZULIP_TOPIC)
    return request

def zulip_read_payload() -> dict:
    request = {
        'anchor': 'newest',
        'num_before': 5,
        'num_after': 5,
        'narrow': [{'operator': settings.ZULIP_TYPE, 'operand': settings.ZULIP_TARGET}],
    }
    return request

def zulip_client():
    return zulip.Client(
        email=settings.ZULIP_MAIL,
        site=settings.ZULIP_URL,
        api_key=settings.ZULIP_KEY
    )