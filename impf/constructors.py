import os
import platform
import logging
import locale
from datetime import datetime
from typing import List

from selenium.webdriver.chrome.options import Options
import settings

logger = logging.getLogger(__name__)

try:
    locale.setlocale(locale.LC_TIME, "de_DE")
except locale.Error:
    pass

try:
    import zulip
except ModuleNotFoundError:
    if settings.ZULIP_ENABLED: logger.warning('Zulip package not found, but ZULIP_ENABLED configured '
                                              '- cannot send alerts via zulip until package is installed')

class AdvancedSessionError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return f'AdvancedSessionError({self.code!r}, {self.message!r})'

    def __str__(self):
        return f'[{self.code}] {self.message}'

class AdvancedSessionCache(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message

    def __repr__(self):
        return f'AdvancedSessionCache({self.code!r}, {self.message!r})'

    def __str__(self):
        return f'Cookies likely expired – [{self.code}] {self.message}'


def browser_options():
    """ Helper function to build Selenium Browser options """
    opts = Options()
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    if settings.SELENIUM_DEBUG: opts.add_argument('--auto-open-devtools-for-tabs')
    if settings.USER_AGENT != 'default': opts.add_argument(f'user-agent={settings.USER_AGENT}')
    # Fallback, falls Chrome Installation in Program Files installiert ist
    if settings.CHROME_PATH: opts.binary_location = settings.CHROME_PATH
    if not settings.CONCURRENT_ENABLED:
        opts.add_argument(f'--user-data-dir={os.path.join(os.getcwd(), "selenium")}')  # Used for persistent cookies
        opts.add_argument('--profile-directory=Default')
    if os.environ.get('DOCKER_ENV'):
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--no-sandbox')
    return opts


def _format_appointments(appointment: list) -> str:
    """ Helper function for formatting an appointment """
    s = []
    for a in appointment:
        s.append(
            datetime.fromtimestamp(a.get('begin') / 1000).strftime('%a, %d.%m.%Y - %H:%M Uhr')
        )
    return ' x '.join(s)


def format_appointments(raw_appointments: list) -> List[str]:
    """ Formats appointments of the REST API to actionable entries """
    appointments = []
    for i, appointment in enumerate(raw_appointments):
        appointments.append(
            f'- {_format_appointments(appointment)} (appt:{i + 1})'
        )
    return appointments


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
            'operator': settings.ZULIP_TYPE if settings.ZULIP_TYPE == 'stream' else 'sender',
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