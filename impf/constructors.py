import platform
import zulip

import settings


def get_command() -> str:
    """ Helper function to return command """
    if settings.COMMAND_LINE: return settings.COMMAND_LINE
    # Command not configured; let's use a fallback to alert the user
    if platform.system() == 'Linux': return 'echo "ALARM ALARM ALARM"|espeak'
    if platform.system() == 'Windows': return 'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'ALARM ALARM ALARM\');"'
    if platform.system() == 'Darwin': return 'say "ALARM ALARM ALARM"'
    return ''


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