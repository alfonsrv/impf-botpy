import concurrent.futures
from time import sleep
from datetime import datetime, timedelta
import logging

import settings
from impf.browser import Browser

logger = logging.getLogger(__name__)
b = None  # helper variable for keeping browser open

def print_config() -> None:
    print('[x] General')
    print(f'- Age: {settings.AGE}')
    print(f'- Mail: {settings.MAIL}')
    print(f'- Mobile: {settings.PHONE}')
    print(f'- Centers: {len(settings.LOCATIONS)} locations')
    print('[x] Alerting Methods')
    if settings.COMMAND_ENABLED: print('- Custom Command ✓')
    if settings.ZULIP_ENABLED: print('- Zulip ✓')

def impf_me(location):
    """ Helper function to support concurrency """
    global b  # Open Browser Helper variable
    x = b or Browser(**location)

    # Keep Browser open
    if settings.KEEP_BROWSER and not (settings.CONCURRENT_ENABLED) and b is None:
        logger.info('Keeping Browser open')
        x.keep_browser = True
        b = x

    # Continue with normal loop
    x.control_main()
    logger.info(f'Waiting until {(datetime.now() + timedelta(seconds=settings.WAIT_LOCATIONS)).strftime("%H:%M:%S")} '
                f'before checking the next location')
    sleep(settings.WAIT_LOCATIONS)


if __name__ == '__main__':
    logger.info('Starting up Impf Bot.py - @alfonsrv, 05/2021')
    print_config()

    while True:
        if settings.CONCURRENT_ENABLED:
            with concurrent.futures.ThreadPoolExecutor(max_workers=settings.CONCURRENT_WORKERS) as executor:
                _ = executor.map(impf_me, settings.LOCATIONS)
        else:
            for location in settings.LOCATIONS:
                impf_me(location)