from time import sleep

import settings
from impf.alert import zulip_read
from impf.browser import Browser

if __name__ == '__main__':
    print('Starting up Impf Bot.py - @alfonsrv, 05/2021')
    for location in settings.LOCATIONS:
        x = Browser(**location)
        x.control_main()
        sleep(settings.WAIT_LOCATIONS)

