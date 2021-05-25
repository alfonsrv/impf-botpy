import argparse
import concurrent.futures
from concurrent.futures import FIRST_COMPLETED
from time import sleep
from datetime import datetime, timedelta
import logging

import settings
from impf import __version__ as v
from impf.alert import send_alert
from impf.api import API
from impf.browser import Browser

logger = logging.getLogger(__name__)
b = None  # helper variable for keeping browser open


def print_config() -> None:
    print('[x] General')
    print(f'- Age: {settings.AGE}')
    print(f'- Mail: {settings.MAIL}')
    print(f'- Mobile: +49{settings.PHONE}')
    print(f'- Centers: {len(settings.LOCATIONS)} locations')
    print(f'[x] Remote Booking {"ENABLED" if settings.BOOK_REMOTELY else "DISABLED"}')
    if settings.BOOK_REMOTELY:
        print('Appointments will be booked for:')
        print(f'- {settings.SALUTATION} {settings.FIRST_NAME} {settings.LAST_NAME}')
        print(f'- {settings.STREET_NAME} {settings.HOUSE_NUMBER}')
        print(f'- {settings.ZIP_CODE} {settings.CITY}')
    print('[x] Alerting Methods')
    if settings.COMMAND_ENABLED: print('- Custom Command ✓')
    if settings.ZULIP_ENABLED: print('- Zulip ✓')
    if settings.TELEGRAM_ENABLED: print('- Telegram ✓ (only sending)')
    if settings.PUSHOVER_ENABLED: print('- Pushover ✓')


def print_version() -> None:
    print(v)


def instant_code() -> None:
    print('Before a Vermittlungscode can be generated, you must specify your '
          'phone number, email and the location in `settings.py`\n')
    print('The bot is hard-coded to only request BioNTech + Moderna (18-60yo)')
    print('Should you request a vaccination for an older demographic or prefer another vaccination '
          'this method won\'t work for you.\n')
    print('Please note: This is an experimental feature and may break at any time.')
    print('If it breaks, please just fall back to using the browser instead.\n\n')
    zip_code = input('Enter the zip code or partial name of the location you require a Vermittlungscode for: ')
    location = ''
    for _location in settings.LOCATIONS:
        if zip_code in _location['location']:
            location = _location['location']
            break

    if not location or not location[:5].isdigit():
        print(f'Location {location} not found or ZIP code ({location[:5]}) not formatted properly')
        return

    print(f'Requesting Instant Vermittlungscode for location {location}...')
    x = Browser(location=location, code='')
    x.main_page()
    x.waiting_room()
    x.location_page()
    a = API(driver=x)
    x.driver.close()

    token = a.generate_vermittlungscode()
    if not token: return

    sms_pin = input('Please enter the SMS code you got via SMS: ').strip().replace('-', '')
    if a.verify_token(token=token, sms_pin=sms_pin):
        print('OK! Please check your emails and enter the code for the correlating location')
    else:
        print('Token could not be verified – did you enter the right SMS PIN?')


def impf_me(location: dict):
    """ Helper function to support concurrency """
    global b  # Open Browser Helper variable
    x = b or Browser(**location)

    # Keep Browser open
    if settings.KEEP_BROWSER and not (settings.CONCURRENT_ENABLED):
        if b is None:
            logger.info('Keeping Browser open; KEEP_BROWSER is set to True')
            x.keep_browser = True
            b = x
        else:
            x.reinit(**location)

    # Continue with normal loop
    x.control_main()

    logger.info(f'Waiting until {(datetime.now() + timedelta(seconds=settings.WAIT_LOCATIONS)).strftime("%H:%M:%S")} '
                f'before checking the next location')
    sleep(settings.WAIT_LOCATIONS)
    if not x.keep_browser: x.driver.close()
    return location


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alerts', help='Check all alert backends and exit', action='store_true')
    parser.add_argument('--code', help='Instant Vermittlungscode Generator', action='store_true')
    parser.add_argument('--version', help='Print version and exit', action='store_true')
    args = parser.parse_args()

    if args.version: print_version(); exit()
    if args.alerts: print_config(); send_alert('Notification test from Impf Bot.py - https://github.com/alfonsrv/impf-botpy'); exit()

    logger.info(f'Starting up Impf Bot.py - github/@alfonsrv, 05/2021 (version {v})')
    if args.code: instant_code(); exit()
    print_config()

    while True:
        if settings.CONCURRENT_ENABLED:
            logger.info(f'CONCURRENT_ENABLED set with {settings.CONCURRENT_WORKERS} simultaneous workers')
            logger.info(f'Spawning Browsers with {settings.WAIT_CONCURRENT}s delay.')
            locations = settings.LOCATIONS
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.CONCURRENT_WORKERS) as executor:
                # futures = [executor.submit(impf_me, location) for location in settings.LOCATIONS]10
                futures = []
                for location in settings.LOCATIONS:
                    futures.append(executor.submit(impf_me, location))
                    sleep(settings.WAIT_CONCURRENT)

                while futures:
                    done, _ = concurrent.futures.wait(futures, return_when=FIRST_COMPLETED)

                    for future in done:
                        futures.remove(future)
                        _location = future.result()
                        futures.append(executor.submit(impf_me, _location))

        else:
            for location in settings.LOCATIONS:
                impf_me(location)
