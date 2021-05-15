from typing import List, Dict

# EDIT ME HERE WITH YOUR DATA
BUNDESLAND: str = 'Baden-Württemberg'
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

AGE: str = '30'
# after the +49 // after the 0
PHONE: str = '1514201337'
MAIL: str = 'erst-mal@ent-spahnen.de'


# Seconds before checking next location
WAIT_LOCATIONS: int = 60*5  # 5 Min
# Seconds to wait for manual SMS input, if no
# Zulip message is received or configured
WAIT_SMS_MANUAL: int = 60*9  # 9 Min
# Seconds to wait for page to load and elements to show
WAIT_BROWSER_MAXIMUM: int = 10


# Chromium Driver Path - leave empty to use auto detect
# OS examples for common paths - e.g.
# Ubuntu: /usr/lib/chromium-browser/chromedriver
# Windows: C:/ProgramData/chocolatey/bin/chromedriver.exe
SELENIUM_PATH: str = ''
# Open Chrome Developer Tab?
# Clicking on Network allows you to get more information - if server
# returns <429>, you're making too many requests and it times you out
SELENIUM_DEBUG: bool = True

# User Agent to use. Use 'default' to not alter the Browser's user agent manually
USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'


# ALERTING SETTINGS
ALERT_TEXT = 'Neuer Impftermin in {{ LOCATION }}! SMS Code innerhalb der nächsten 10 Minuten übermitteln. (sms:123-456)'

# Run a custom command when a new appointment is found (e.g. audio alerts) - Text-to-Speech
# Windows: 'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'ALARM ALARM ALARM\');"'
# macOS: 'say "ALARM ALARM ALARM"'
# Debian: 'echo "ALARM ALARM ALARM"|espeak'
COMMAND_ENABLED = True
COMMAND_LINE = 'echo "ALARM ALARM ALARM"|espeak'


# Zulip (https://chat.zulip.org/api/)
ZULIP_ENABLED = False
ZULIP_URL = 'https://chat.zulip.org/'
ZULIP_MAIL = 'bot@domain.tld'
ZULIP_KEY = 'secret-key'
ZULIP_TYPE = 'stream'  # private, stream
ZULIP_TARGET = 'hunter'
ZULIP_TOPIC = 'General'