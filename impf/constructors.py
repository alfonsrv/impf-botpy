import os
import platform
import logging

from selenium.webdriver.chrome.options import Options
import settings

logger = logging.getLogger(__name__)

try:
    import zulip
except ModuleNotFoundError:
    if settings.ZULIP_ENABLED: logger.warning('Zulip package not found, but ZULIP_ENABLED configured '
                                              '- cannot send alerts via zulip until package is installed')


def browser_options():
    """ Helper function to build Selenium Browser options """
    opts = Options()
    if settings.SELENIUM_DEBUG: opts.add_argument('--auto-open-devtools-for-tabs')
    if settings.USER_AGENT != 'default': opts.add_argument(f'user-agent={settings.USER_AGENT}')
    # Fallback, falls Chrome Installation in Program Files installiert ist
    if settings.CHROME_PATH: opts.binary_location = settings.CHROME_PATH
    if os.environ.get('DOCKER_ENV'):
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
    return opts


def get_command() -> str:
    """ Helper function to return command """
    if settings.COMMAND_LINE: return settings.COMMAND_LINE
    # Command not configured; let's use a fallback to alert the user
    if platform.system() == 'Linux': return 'echo "ALARM ALARM ALARM"|espeak'
    if platform.system() == 'Windows': return 'PowerShell -Command "Add-Type –AssemblyName System.Speech; ' \
                                              '(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'ALARM ALARM ALARM\');"'
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
        'narrow': [{
            'operator': settings.ZULIP_TYPE,
            'operand': settings.ZULIP_TARGET
        }],
    }
    return request


def zulip_client():
    try:
        return zulip.Client(
            email=settings.ZULIP_MAIL,
            site=settings.ZULIP_URL,
            api_key=settings.ZULIP_KEY
        )
    except:
        logger.exception('An error occurred trying to instantiate Zulip Client')
        return None