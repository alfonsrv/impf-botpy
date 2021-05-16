from typing import List, Dict

# EDIT ME HERE WITH YOUR DATA
BUNDESLAND: str = 'Baden-Württemberg'
# Enter the locations to monitor here; as seen on ImpfterminService. If you have a Vermittlungscode
# for the corresponding location, enter it at `code`, otherwise leave empty. Please be careful when
# editing this. It's easy to make mistakes and prevent the application from starting up; it's
# advisable to just replace the locations with your preferred ones if you're unsure what you're doing.
LOCATIONS: List[Dict[str, str]] = [
    {
        'location': '70174 Stuttgart',
        'code': '',
    }, {
        'location': '70376 Stuttgart',
        'code': ''
    }, {
        'location': '71636 Ludwigsburg',
        'code': 'Q123-ABCD-C0DE'
    }, {
        'location': '75175 Pforzheim',
        'code': ''
    },
]

AGE: str = '27'
# after the +49 // after the 0
PHONE: str = '1514201337'
MAIL: str = 'erst-mal@ent-spahnen.de'


# > Waiting Times
# ----------------------
# Seconds before checking next location
WAIT_LOCATIONS: int = 60*5  # 5 Min
# Seconds to wait for manual SMS input, if no
# Zulip message is received or configured
WAIT_SMS_MANUAL: int = 60*9  # 9 Min
# Seconds to wait for page to load and elements to show
WAIT_BROWSER_MAXIMUM: int = 10


# > Advanced Features
# ----------------------
CONCURRENT_ENABLED: bool = False
CONCURRENT_WORKERS: int = 3
# Keep the same browser window for checking all locations; makes it easier to run in background
# Cannot be used in combination with `CONCURRENT_ENABLED`
KEEP_BROWSER: bool = True

# Chromium Driver Path - leave empty to use auto detect
# OS examples for common paths - e.g.
# Ubuntu: /usr/lib/chromium-browser/chromedriver
# Windows: C:/ProgramData/chocolatey/bin/chromedriver.exe
SELENIUM_PATH: str = ''
# Open Chrome Developer Tab? - Recommended to set to true
# Clicking on Network allows you to keep an eye on what's going on - if the server returns
# status code <429>, you're making too many requests and it *shadow bans* you temporarily
SELENIUM_DEBUG: bool = False

# User Agent to use. Use 'default' to not alter the Browser's user agent manually
# can be se to e.g. 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
USER_AGENT: str = 'default'


# ALERTING SETTINGS
ALERT_TEXT = 'Neuer Impftermin in {{ LOCATION }}! SMS Code innerhalb der nächsten 10 Minuten übermitteln. (sms:123-456)'

# Run a custom command when a new appointment is found (e.g. audio alerts)
# Text-to-Speech examples
# - Windows: 'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'ALARM ALARM ALARM\');"'
# - macOS: 'say "ALARM ALARM ALARM"'
# - Debian: 'echo "ALARM ALARM ALARM"|espeak'
COMMAND_ENABLED: bool = True
COMMAND_LINE: str = ''


# Zulip (https://chat.zulip.org/api/)
ZULIP_ENABLED: bool = False
ZULIP_URL: str = 'https://chat.zulip.org/'
ZULIP_MAIL: str = 'bot@domain.tld'
ZULIP_KEY: str = 'secret-key'
ZULIP_TYPE: str = 'stream'  # private, stream
ZULIP_TARGET: str = 'hunter'
ZULIP_TOPIC: str = 'General'


# DO NOT EDIT
import os
import logging
import logging.handlers

# Set to logging.WARNING to minimal output
LOG_LEVEL = logging.INFO  # logging.DEBUG // .ERROR...


os.chdir(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))
WORK_DIR = os.getcwd()
LOG_FILE = ''
IMPF_FORMAT = '%(asctime)s - %(location)s: $(message)s'

LOG_PATH = os.path.join(WORK_DIR, LOG_FILE or 'bot.log')
logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] <%(name)s.%(filename)s:%(lineno)s>  %(message)s',
    level=LOG_LEVEL,
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            LOG_PATH,
            maxBytes=1024 * 1024,   # 1 MB
            backupCount=1
        )
    ]
)

class LocationAdapter(logging.LoggerAdapter):
    """ Custom adapter to easily add PLZ to log string """
    def process(self, msg, kwargs):
        return '%s: %s' % (self.extra['location'], msg), kwargs