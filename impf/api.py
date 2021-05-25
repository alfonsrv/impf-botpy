from base64 import b64encode
from dataclasses import dataclass, field
from time import sleep
from typing import Any, List, Dict, Union
from urllib.parse import urlparse
import logging

from requests.sessions import Session
import settings
from impf.constructors import AdvancedSessionError, AdvancedSessionCache
from impf.decorators import api_call, next_gen

logger = logging.getLogger(__name__)

@dataclass
class AdvancedSession:
    session = None
    error_counter = 0
    logger: 'logger' = field(init=False)

    def __post_init__(self):
        self.session = Session()

        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
                            if settings.USER_AGENT == 'default' else settings.USER_AGENT,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, br',
        })

        self.logger = settings.LocationAdapter(logger, {'location': 'API'})

    @api_call
    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self.session.get(*args, **kwargs)

    @api_call
    def post(self, *args: Any, **kwargs: Any) -> Any:
        return self.session.post(*args, **kwargs)

    def _handle_error(self, code: int, message: dict) -> None:
        self.error_counter += 1
        if self.error_counter >= 3:
            raise AdvancedSessionError(-1, 'Maximum retries exceeded')
        elif code == 429:
            self.logger.warning('[429] The server is experiencing too many requests – either from our IP or generally. '
                           f'Waiting {settings.WAIT_API_CALLS // 60}min before trying again')
            self.logger.warning('It is highly recommended to avoid any further activity and stop '
                                'requesting ImpfterminService during that time')
            sleep(settings.WAIT_API_CALLS)
        elif code >= 400:
            if message:
                if 'Anfragelimit erreicht' in message.get('error'):
                    raise AdvancedSessionError(-1, 'Maximum requests reached for phone number and email')
            self.logger.info('Cookies probably expired – raising AdvancedSessionCache')
            raise AdvancedSessionCache(code, message)
        else:
            import pdb; pdb.set_trace()
            raise AdvancedSessionError(code, message)


@dataclass
class API:
    host: str = field(init=False)
    driver: 'Browser' = None
    xs: AdvancedSession = None  # requests.Session
    logger: 'logger' = field(init=False)
    _zip_code: str = ''
    _code: str = ''

    def __post_init__(self):
        self.xs = AdvancedSession()
        if self.driver is not None:
            _host = urlparse(self.driver.driver.current_url)
            self.host = f'{_host.scheme}://{_host.hostname}'
            self.xs.session.cookies.update({c['name']: c['value'] for c in self.driver.driver.get_cookies()})
        self.logger = settings.LocationAdapter(logger, {'location': 'API'})
        if not self.cookies_complete:
            self.logger.info('Caution! You might not have all cookies to issue requests!')

    @property
    def zip_code(self) -> str:
        if self._zip_code: return self._zip_code
        if self.driver is None: return ''
        _zip_code = self.driver.location[:5]
        assert _zip_code.isdigit()
        return _zip_code

    @zip_code.setter
    def zip_code(self, value: str) -> None:
        """ Probably not required; just here so everyone knows
                 I'm pretty good with setters too """
        if not isinstance(value, str):
            self.logger.info(f'ZIP code must be str – got {type(value)} instead!')
            return
        self._zip_code = value

    @property
    def code(self) -> str:
        if self._code: return self._code
        if self.driver is None: return ''
        return self.driver.code

    @code.setter
    def code(self, value: str) -> None:
        """ Probably not required; just here so everyone knows
                 I'm pretty good with setters too """
        if not isinstance(value, str):
            self.logger.info(f'Vermittlungscode must be str – got {type(value)} instead!')
            return
        self._code = value

    @property
    def cookies_complete(self) -> bool:
        cookies = ['bm_sz', 'bm_mi', 'ak_bmsc' , '_abck', 'bm_sv', 'akavpau_User_allowed']
        missing = [cookie for cookie in cookies if cookie not in self.xs.session.cookies.get_dict().keys()]
        if missing: self.logger.info(f'Potentially missing cookies: {missing}')
        return not(missing)

    def auth(self) -> None:
        """ Sets Authorization Header """
        self.xs.session.headers.update({
            'Authorization': f'Basic {b64encode(f":{self.code}".encode("utf-8")).decode("utf-8")}',
            'Referer': f'{self.host}/impftermine/suche/{self.code}/{self.zip_code}'
        })

    def refresh_cookies(self) -> None:
        from .browser import Browser
        x = Browser(location=self.zip_code, code=self.code)
        x.main_page()
        x.location_page()
        self.xs.session.cookies.update({c['name']: c['value'] for c in x.driver.get_cookies()})
        x.driver.quit()

    @next_gen
    def generate_vermittlungscode(self) -> str:
        """ Generiert Vermittlungscode via REST API Call """
        self.logger.info('Attempting to get Vermittlungscode from server')
        data = {
            'email': settings.MAIL,
            'leistungsmerkmal': 'L921',  # BioNTech, Moderna
            'phone': f'+49{settings.PHONE}',
            'plz': self.zip_code
        }

        try:
            r = self.xs.post(f'{self.host}/rest/smspin/anforderung', json=data)
        except AdvancedSessionError:
            if not self.cookies_complete:
                self.logger.warning('You do not seem to have all cookies. Please first enrich your cookies by letting '
                                  'the bot run for 1-2h with `CONCURRENT_ENABLED = False` and `KEEP_BROWSER = True`')
                self.logger.warning('Alternatively you can run the bot interactively using `python main.py --surf` and '
                                    'click around a bit manually for ~45min to attempt and acquire the cookies.')
            self.logger.error('Could not generate code – please try again later.')
            return

        if not r.json().get("token"):
            self.logger.error(f'An error occurred requesting Instant Vermittlungscode from server – didn\'t get token from server')
            self.logger.info(f'Response: [{r.status_code}] {r.text}')

        return r.json().get("token")

    @next_gen
    def verify_token(self, token: str, sms_pin: str) -> bool:
        """ Verifiziert Token via SMS PIN """
        self.logger.info(f'Verifying Vermittlungscode with SMS PIN "{sms_pin}"')
        data = {
            'token': token,
            'smspin': sms_pin
        }

        r = self.xs.post(f'{self.host}/rest/smspin/verifikation', json=data)
        return r.status_code == 200

    @next_gen
    def get_appointments(self) -> dict:
        params = {
            'plz': self.zip_code
        }
        return self.xs.get(f'{self.host}/rest/suche/impfterminsuche', params=params).json()

    @next_gen
    def book_appointment(self, appointments: Dict, idx: int) -> bool:
        """ Bucht Appointment mit Index idx-1 """
        self.logger.info(f'Booking appointment for {self.zip_code}')

        data = {
            'slots': [termin.get("slotId") for termin in appointments.get('termine')[idx-1]],
            'qualifikationen': appointments.get('gesuchteLeistungsmerkmale'),
            'plz': self.zip_code,
            'contact': {
                'anrede': settings.SALUTATION,
                'vorname': settings.FIRST_NAME,
                'nachname': settings.LAST_NAME,
                'strasse': settings.STREET_NAME,
                'hausnummer': settings.HOUSE_NUMBER,
                'plz': settings.ZIP_CODE,
                'ort': settings.CITY,
                'phone': f'+49 {settings.PHONE}',
                'notificationReceiver': settings.MAIL,
                'notificationChannel': 'email'
            },
        }
        r = self.xs.post(f'{self.host}/rest/buchung', json=data)

        if r.status_code == 481:
            self.logger.info('Code was already used to book an appointment')
            return False
        # Only relevant Request – explicit logging for debugging purposes and user issues
        self.logger.info(f'[{r.status_code}] {r.text}')
        return r.status_code == 201

    def control_appointments(self) -> dict:
        """ Hilfsfunktion um Appointments via REST API vom Backend zu laden """
        try:
            self.auth()
            appointments = self.get_appointments()
        except:
            self.logger.exception('An exception occurred while loading appointments via REST API!')
            appointments = []
        return appointments