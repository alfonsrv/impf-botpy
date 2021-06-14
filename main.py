import argparse
import concurrent.futures
from concurrent.futures import FIRST_COMPLETED
from time import sleep
from datetime import datetime, timedelta
import logging
try: import readline
except: pass

import settings
from impf import __version__ as v
from impf.alert import send_alert
from impf.api import API
from impf.browser import Browser

logger = logging.getLogger(__name__)
b = None  # helper variable for keeping browser open


def print_config() -> None:
    print('[x] General')
    print(f'- Birthday: {settings.BIRTHDATE}')
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
    if settings.TELEGRAM_ENABLED: print('- Telegram ✓')
    if settings.PUSHOVER_ENABLED: print('- Pushover ✓')
    if settings.GOTIFY_ENABLED: print('- Gotify ✓')
    print('[x] Locations')
    for location in settings.LOCATIONS:
        print(f'- {location["location"]}: {location["code"] if location["code"] else "No code configured"}')


def print_version() -> None:
    print(v)


def instant_code() -> None:
    print('Before a Vermittlungscode can be generated, you must specify your '
          'phone number, email and the location in `settings.py`\n')
    print('The bot is hard-coded to only request BioNTech + Moderna (18-60yo)')
    print('Should you request a vaccination for an older demographic or prefer another vaccine '
          'this method won\'t work for you.\n')
    print('Please note: This feature may break at any time – use it while you can!')
    print('If it breaks, please just fall back to using the browser instead.\n\n')
    zip_code = input('Enter the zip code of the location you require a Vermittlungscode for: ')

    center = API.zip_center(zip_code)
    if not center: print(f'Center with zip code "{zip_code}" not found'); return
    print(f'Requesting Vermittlungscode for: {center.get("Zentrumsname").strip()}, {center.get("PLZ")} {center.get("Ort")}')

    if args.manual:
        print(f'URL: {center.get("URL")}impftermine/service?plz={zip_code}')
        c = input(f'Input cookies: ')
        api = API.manual(center.get("URL"), c)
        api.zip_code = zip_code
    else:
        x = Browser(location=zip_code, code='')
        x.main_page()
        x.waiting_room()
        x.inject_session()
        x.location_page()
        x.driver.get(f'https://{x.server_id}-iz.impfterminservice.de/impftermine/check')
        x.claim_code()

        input('Please continue manually... press Enter to continue trying via API if this doesn\'t work! (Press CTRL+C to exit) ')

        api = API(driver=x)
        x.driver.close()

    token = api.generate_vermittlungscode()
    if not token: return

    sms_pin = input('Please enter the SMS code you got via SMS: ').strip().replace('-', '')
    if api.verify_token(token=token, sms_pin=sms_pin):
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
    try: x.control_main()
    except RecursionError: pass

    logger.info(f'Waiting until {(datetime.now() + timedelta(seconds=settings.WAIT_LOCATIONS)).strftime("%H:%M:%S")} '
                f'before checking the next location')
    sleep(settings.WAIT_LOCATIONS)
    if not x.keep_browser: x.driver.quit()
    return {'location': x.location, 'code': x.code}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alerts', help='Check all alert backends and exit', action='store_true')
    parser.add_argument('--code', help='Instant Vermittlungscode Generator (works best from 23:00 to 07:00)', action='store_true')
    parser.add_argument('--manual', help='Undocumented super function', action='store_true')
    parser.add_argument('--surf', help='Interactive Surf Session for Cookie Enrichment', action='store_true')
    parser.add_argument('--version', help='Print version and exit', action='store_true')
    args = parser.parse_args()

    if args.version: print_version(); exit()
    if args.alerts: print_config(); send_alert('Notification test from Impf Bot.py - https://github.com/alfonsrv/impf-botpy'); exit()

    logger.info(f'Starting up Impf Bot.py - github/@alfonsrv, 05/2021 (version {v})')
    if args.code: instant_code(); exit()
    if args.manual: print('Try in combination with --code'); exit()
    elif args.surf: x = Browser(location='', code=''); input('Press Enter to end interactive session'); x.driver.quit(); exit()
    print_config()

    if settings.CONCURRENT_ENABLED:
        logger.info(f'CONCURRENT_ENABLED set with {settings.CONCURRENT_WORKERS} simultaneous workers')
        logger.info(f'Spawning Browsers with {settings.WAIT_CONCURRENT}s delay.')
        locations = settings.LOCATIONS
        with concurrent.futures.ThreadPoolExecutor(max_workers=settings.CONCURRENT_WORKERS) as executor:
            # futures = [executor.submit(impf_me, location) for location in settings.LOCATIONS]
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
                    del future

    else:
        while True:
            for location in settings.LOCATIONS:
                _location = impf_me(location)

                # If Vermittlungscode is invalid/already used, it is unset during Browser
                # runtime, let's make sure we unset it for the next iteration
                if _location.get('code') != location.get('code'):
                    # Get Index of Location in settings-Location List
                    idx = next((index for (index, d) in enumerate(settings.LOCATIONS)
                                if d["location"] == location['location']
                                and d['code'] == location['code']),
                               None)
                    if idx: settings.LOCATIONS[idx]['code'] = ''
