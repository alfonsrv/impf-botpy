from datetime import datetime, timedelta
from time import sleep
import logging

import settings

logger = logging.getLogger(__name__)

def sleep_bot() -> bool:
    """ Helper function to sleep bot during night"""
    now = datetime.now()
    if settings.SLEEP_NIGHT and (now.hour >= 23 or now.hour < 6):
        logger.info('SLEEP_NIGHT enabled and current time is between 2300-0600; pausing bot')
        while now.hour >= 23 or now.hour < 6:
            sleep(120)
        logger.info('Resuming Impf Bot.py!')
        return True
    return False

def shadow_ban(func):
    """ Decorator um Shadow Ban autom. zu vermeiden """

    def f(self, *args, **kwargs):
        if sleep_bot(): return self.control_main()
        x = func(self, *args, **kwargs)
        shadow_ban = self.too_many_requests
        if shadow_ban:
            self.logger.warning('Sending too many requests - got `429` from server!')
            if not settings.AVOID_SHADOW_BAN: self.logger.info('AVOID_SHADOW_BAN not enabled; continuing without waiting')
            self.error_counter += 1
            while self.error_counter <= 4 and shadow_ban and settings.AVOID_SHADOW_BAN:
                wait_time = settings.WAIT_SHADOW_BAN + (2 * 60 * self.error_counter)
                self.logger.info(f'[{self.error_counter}/5] Attempting to recover from shadow ban by waiting until '
                                 f'{(datetime.now() + timedelta(seconds=wait_time)).strftime("%H:%M:%S")} ({wait_time // 60}min)')

                self.error_counter += 1
                sleep(wait_time)
                self.wiggle_recover()
                x = func(self, *args, **kwargs)
                shadow_ban = self.too_many_requests

            if not shadow_ban: self.error_counter = 0
            else: self.control_main()

        return x
    return f