from datetime import datetime, timedelta
from time import sleep

import settings


def shadow_ban(func):
    """ Decorator um Shadow Ban autom. zu vermeiden """

    def f(self, *args, **kwargs):
        x = func(self, *args, **kwargs)
        if self.too_many_requests:
            self.logger.warning('Sending too many requests - got `429` from server!')
            if not settings.AVOID_SHADOW_BAN: self.logger.info('AVOID_SHADOW_BAN not enabled; continuing without waiting')
            while self.error_counter <= 5 and self.too_many_requests and settings.AVOID_SHADOW_BAN:
                wait_time = settings.WAIT_SHADOW_BAN + (60 * self.error_counter)
                self.logger.info(f'Attempting to recover from shadow ban by waiting until '
                                 f'{(datetime.now() + timedelta(seconds=wait_time)).strftime("%H:%M:%S")}')
                self.error_counter += 1
                sleep(wait_time)
                x = func(self, *args, **kwargs)
        return x
    return f