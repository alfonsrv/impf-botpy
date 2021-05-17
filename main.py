import argparse
import concurrent.futures
from concurrent.futures import FIRST_COMPLETED
from time import sleep
from datetime import datetime, timedelta
import logging

import settings
from impf.alert import send_alert
from impf.browser import Browser

logger = logging.getLogger(__name__)
b = None  # helper variable for keeping browser open

def print_config() -> None:
    print('[x] General')
    print(f'- Age: {settings.AGE}')
    print(f'- Mail: {settings.MAIL}')
    print(f'- Mobile: +49{settings.PHONE}')
    print(f'- Centers: {len(settings.LOCATIONS)} locations')
    print('[x] Alerting Methods')
    if settings.COMMAND_ENABLED: print('- Custom Command ✓')
    if settings.ZULIP_ENABLED: print('- Zulip ✓')

def print_version() -> None:
    from impf import __version__ as v
    print(v)

def impf_me(location):
    """ Helper function to support concurrency """
    global b  # Open Browser Helper variable
    x = b or Browser(**location)

    # Keep Browser open
    if settings.KEEP_BROWSER and not (settings.CONCURRENT_ENABLED):
        if b is None:
            logger.info('Keeping Browser open; KEEP_BROWSER is set to True')
            x.keep_browser = True
            b = x
        else: x.reinit(**location)

    # Continue with normal loop
    x.control_main()

    logger.info(f'Waiting until {(datetime.now() + timedelta(seconds=settings.WAIT_LOCATIONS)).strftime("%H:%M:%S")} '
                f'before checking the next location')
    sleep(settings.WAIT_LOCATIONS)
    return location


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--alerts', help='Check all alert backends and exit', action='store_true')
    parser.add_argument('--version', help='Print version and exit', action='store_true')
    args = parser.parse_args()

    if args.version: print_version(); exit()
    if args.alerts: print_config(); send_alert('Notification test from Impf Bot.py - https://github.com/alfonsrv/impf-botpy'); exit();

    logger.info('Starting up Impf Bot.py - github/@alfonsrv, 05/2021')
    print_config()

    while True:
        if settings.CONCURRENT_ENABLED:
            logger.info(f'CONCURRENT_ENABLED set with {settings.CONCURRENT_WORKERS} simultaneous workers')
            logger.info(f'Spawning Browsers with {settings.WAIT_CONCURRENT}s delay.')
            locations = settings.LOCATIONS
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.CONCURRENT_WORKERS) as executor:
                #futures = [executor.submit(impf_me, location) for location in settings.LOCATIONS]10
                futures = []
                for location in settings.LOCATIONS:
                    futures.append(executor.submit(impf_me, location))
                    sleep(30)

                while futures:
                    done, _ = concurrent.futures.wait(futures, return_when=FIRST_COMPLETED)

                    for future in done:
                        futures.remove(future)
                        _location = future.result()
                        futures.append(executor.submit(impf_me, _location))

        else:
            for location in settings.LOCATIONS:
                impf_me(location)