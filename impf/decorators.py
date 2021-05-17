from datetime import datetime, timedelta
from time import sleep

import settings

def shadow_ban(func):
    """ Decorator um Shadow Ban autom. zu vermeiden """

    def f(self, *args, **kwargs):
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