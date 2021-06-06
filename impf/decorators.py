from datetime import datetime, timedelta
from time import sleep
import logging

from requests import Timeout, ConnectionError
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

import settings
from impf.exceptions import AdvancedSessionCache, AlertError, WorkflowException

logger = logging.getLogger(__name__)


def sleep_bot() -> bool:
    """ Helper function to sleep bot during night"""
    now = datetime.now()
    if settings.SLEEP_NIGHT and (now.hour >= 23 or now.hour < 6):
        logger.info('SLEEP_NIGHT enabled and current time is between 2300-0600; pausing bot')
        while now.hour >= 23 or now.hour < 6:
            sleep(120)
            now = datetime.now()
        logger.info('Resuming Impf Bot.py!')
        return True
    return False


def shadow_ban(f):
    """ Decorator um Shadow Ban autom. zu vermeiden """

    def func(self, *args, **kwargs):
        if sleep_bot():
            self.error_counter = 0
            self.control_main()
            raise WorkflowException('Resetting after recovering from sleep!')

        x = f(self, *args, **kwargs)

        shadow_ban = self.too_many_requests  # oh Python 3.8...
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
                x = f(self, *args, **kwargs)
                shadow_ban = self.too_many_requests

            if not shadow_ban: self.error_counter = 0
            else: raise WorkflowException('Recovering from shadow ban failed!')

        return x
    return func


def control_errors(f):
    """ Decorator to centrally coordinate error handling of control functions"""
    def func(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except StaleElementReferenceException:
            self.logger.warning('StaleElementReferenceException - something happened in the webpage')
            self.logger.error('Sleeping for 120s before continuing, giving the user the '
                              'ability to interact before attempting to revover automatically...')
            sleep(120)
            self.control_assert()
        except AssertionError:
            self.logger.error(f'AssertionError occurred in <{f.__name__}>. This usually happens if your computer/internet '
                              'connection is slow or if the ImpfterminService site changed.')
            self.logger.error('Sleeping for 120s before continuing, giving the user the '
                              'ability to interact before attempting to revover automatically...')
            sleep(120)
            self.control_assert()
        except SystemExit:
            self.logger.warning('Exiting...')
            raise
        except WorkflowException:
            raise
        except:
            self.logger.exception(f'An unexpected exception occurred in <{f.__name__}>')
            if settings.KEEP_BROWSER_CRASH:
                self.logger.exception('KEEP_BROWSER_CRASH configured; keeping browser open post crash')
                self.keep_browser = settings.KEEP_BROWSER_CRASH
            else:
                sleep(10)
            if not self.keep_browser: self.reset()
            raise WorkflowException('Unexpected exception was raised!')

    return func


def alert_resilience(f):
    """ Decorator to make alerts error-resilient """
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AlertError:
            logger.exception(f'The alerting backend <{f.__name__}> returned the wrong value!')
        except:
            logger.exception(f'An unexpected exception occurred in <{f.__name__}> trying to send or read alerts! '
                             'Please report this issue to https://github.com/alfonsrv/impf-botpy/issues')
    return func


def api_call(f):
    """ Decorator for API calls """
    def api_response(self, *args, **kwargs):
        try:
            response = f(self, *args, **kwargs)
        except Timeout:
            self.logger.warning(f'Request timed out <{f.__name__}> (*{args}) (**{kwargs})')
        except ConnectionError:
            self.logger.warning(f'Request timed out <{f.__name__}> (*{args}) (**{kwargs})')
        else:
            self.logger.debug(f'<{f.__name__}> [{response.status_code}] {response.text}')
            if response.status_code in (200, 201, 481):
                return response
            x = self._handle_error(response.status_code, response.json())
            # Rise and Shine (once again) – danke kv.digital
            return x or api_call(f)(self, *args, **kwargs)

    return api_response


def next_gen(f):
    """ Decorator for NextGen Impfservice-specific error handling """
    def func(self, *args, **kwargs):

        try:
            x = f(self, *args, **kwargs)
        except AdvancedSessionCache:
            self.logger.warning(f'Underlying service layer indicating invalid session for <{f.__name__}> – refreshing '
                                f'all cookies and retrying')
            self.xs.session.cookies = {}
            self.refresh_cookies()
            return next_gen(f)(self, *args, **kwargs)
        return x

    return func