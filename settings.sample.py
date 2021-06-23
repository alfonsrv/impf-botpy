from typing import List, Dict

# EDIT ME HERE WITH YOUR DATA
BUNDESLAND: str = 'Baden-Württemberg'
# Enter the locations to monitor here; as seen on ImpfterminService. If you have a Vermittlungscode
# for the corresponding location, enter it at `code`, otherwise leave empty. Please be careful when
# editing this. It's easy to make mistakes and prevent the application from starting up; it's
# advisable to just replace the locations with your preferred ones if you're unsure what you're doing.
# All locations REQUIRE the first five characters to be the center's ZIP code.
LOCATIONS: List[Dict[str, str]] = [
    {
        'location': '70174 Stuttgart',
        'code': '',
    }, {
        'location': '70376 Stuttgart',
        'code': ''
    }, {
        'location': '71636 Ludwigsburg',
        'code': 'Q123-ABCD-C0DE'  # sample Vermittlungscode
    }, {
        'location': '75175 Pforzheim',
        'code': ''
    },
]

# DD.MM.YYYY
BIRTHDATE: str = '31.12.1994'
# after the +49 // after the 0
PHONE: str = '1514201337'
MAIL: str = 'erst-mal@ent-spahnen.de'

# > Appointment Booking
# These settings are not mandatory and only required if you want to book an appointment via Chat app
# ----------------------
# Herr, Frau, Divers, Kind
SALUTATION: str = 'Herr'
FIRST_NAME: str = 'Jens'
LAST_NAME: str = 'Mustermann'
STREET_NAME: str = 'Königsstr.'
HOUSE_NUMBER: str = '1337'
CITY: str = 'Stuttgart'
ZIP_CODE: str = '70173'


# > Waiting Times
# ----------------------
# Seconds before checking next location
WAIT_LOCATIONS: int = 60*5  # 5 Min
# Seconds to wait for manual SMS input, if no
# Zulip message is received or configured
WAIT_SMS_MANUAL: int = 60*10  # 10 Min
# Seconds to wait for page to load and elements to show
WAIT_BROWSER_MAXIMUM: int = 10
# If CONCURRENT_ENABLED browsers will be delayed WAIT_CONCURRENT
# seconds before started to avoid getting `429` directly
WAIT_CONCURRENT: int = 30
# Only relevant if AVOID_SHADOW_BAN is set to True
WAIT_SHADOW_BAN: int = 60*12  # 12 Min
# Seconds to wait time before attempting another API call.
# Only relevant if using instant codes or BOOKING_ENABLED
WAIT_API_CALLS: int = 60*1  # 1 Min
# Seconds to wait before rechecking available appointments.
# Only relevant if RESCAN_APPOINTMENT is set to True
WAIT_RESCAN_APPOINTMENTS: int = 60*2  # 2 Min


# > Basic Features
# ----------------------
# Keep the same browser window for checking all locations; makes it easier to run in background
# Cannot be used in combination with `CONCURRENT_ENABLED` (ignored if CONCURRENT_ENABLED)
KEEP_BROWSER: bool = True
# Checks if the backend is returning error `429` (Too Many Requests) and then sleeps for WAIT_SHADOW_BAN
# seconds before sending the last request again.
AVOID_SHADOW_BAN: bool = True
# Controls whether or not the bot should simply keep on rechecking if new appointments
# are available once we have passed the *Vermittlungscode* and are in the Online Booking screen.
# This is done by clicking "Check for new appointments" after the 10m reservation time runs out
# This can be very useful if you only want to check for one center; however it might also result
# in an undesired behavior; if CONCURRENT_ENABLED is not used the bot will evidently only keep on
# checking only one center over and over again.
RESCAN_APPOINTMENT: bool = True
# Pause bot during night times (2300-0600) since no new appointments are created anyways during
# that time period. Can help reduce shadow bans
SLEEP_NIGHT: bool = True
# Book appointments remotely via Chat app; requires setting all personal data above and configuring at least
# one alert / chat backend. Requires at least one alerting backend to be configured.
# If this feature is disabled, you will still get an audio alert and can book your appointment manually via the browser.
# If this feature is enabled, manual bookings are also still possible.
# Note: This is an experimental feature; but should be stable.
BOOK_REMOTELY: bool = False


# > Advanced Features
# ----------------------
# Check availability with multiple browsers simultaneously
CONCURRENT_ENABLED: bool = False
# How many processes / browsers to use (do not set this number higher
#  than the amount of overall LOCATIONS defined)
CONCURRENT_WORKERS: int = 3
# Keep Browser open after workflow has crashed - helps to debug and possibly save important data;
# however can backfire quickly as it can lead to an infinite amount of Browser windows. Also works
# in combination with CONCURRENT_ENABLED
KEEP_BROWSER_CRASH: bool = False


# Chromium Driver Path - leave empty to use auto detect
# OS examples for common paths - e.g.
# Ubuntu: /usr/lib/chromium-browser/chromedriver
# Windows: C:/ProgramData/chocolatey/bin/chromedriver.exe
SELENIUM_PATH: str = r''
# Open Chrome Developer Tab? - Recommended to set to true
# Clicking on Network allows you to keep an eye on what's going on - if the server returns
# status code <429>, you're making too many requests and it *shadow bans* you temporarily
SELENIUM_DEBUG: bool = False
# Explicitly specify path of chrome executable if Selenium cannot figure it out by itself.
# Read more in `INSTALL.md` under the Windows Troubleshooting section
CHROME_PATH = r''

# User Agent to use. Use 'default' to not alter the Browser's user agent manually
# can be se to e.g. 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
USER_AGENT: str = 'default'


# > Alerting Settings
# ----------------------
ALERT_SMS: str = 'Neuer Vermittlungscode für {{ LOCATION }}! SMS Code innerhalb der nächsten 10 Minuten übermitteln. (sms:123-456)'
ALERT_AVAILABLE: str = 'Impftermine verfügbar in {{ LOCATION }}! Reserviert für die nächsten 10 Minuten... Buchungslink: {{ LINK }}'
ALERT_BOOKINGS: str = ' **Verfügbare Termine:**\n\n{{ APPOINTMENTS }}'

# Run a custom command when a new appointment is found (e.g. audio alerts); if COMMAND_ENABLED is set to True, but no
# command is supplied in COMMAND_LINE, script will automatically fall back to pre-configured Text-to-speech below:
# Text-to-Speech Commands
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

# Telegram (https://core.telegram.org/)
TELEGRAM_ENABLED: bool = False
TELEGRAM_API_TOKEN: str = '1111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
TELEGRAM_CHAT_ID: str = '111111111'

# Slack (https://slack.com)
SLACK_ENABLED: bool = False
SLACK_WEBHOOK_URL: str = 'https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX'

# Pushover (https://pushover.net/)
PUSHOVER_ENABLED: bool = False
PUSHOVER_USER_KEY: str = 'abcdefghijklmnopqrst0123456789'
PUSHOVER_APP_TOKEN: str = '0123456789abcdefghijklmnopqrst'

# Gotify (selfhosted, https://gotify.net/)
GOTIFY_ENABLED: bool = False
GOTIFY_URL: str = 'https://push.example.de:8080'
GOTIFY_APP_TOKEN: str = '111111111111111'

# > Logging Setup
# ----------------------
import logging

# Set to logging.WARNING to minimal output
LOG_LEVEL = logging.INFO  # logging.DEBUG // .ERROR...


# DO NOT EDIT
import os
import logging.handlers
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
