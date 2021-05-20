from dataclasses import dataclass, field
from urllib.parse import urlparse
import logging

from requests.sessions import Session
import settings


@dataclass
class API:
    host: str = field(init=False)
    driver: object = None
    s: Session = None  # requests.Session
    logger: 'logger' = field(init=False)  # Internal adapter-logger to add PLZ field

    def __post_init__(self):
        self.s = Session()
        if self.driver is not None:
            _host = urlparse(self.driver.driver.current_url)
            self.host = f'{_host.scheme}://{_host.hostname}'
            self.s.cookies.update({c['name']: c['value'] for c in self.driver.driver.get_cookies()})
            self.s.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
                                if settings.USER_AGENT == 'default' else settings.USER_AGENT
            })
            self.driver.driver.quit()

        self.logger = logging.getLogger(__name__)

    def generate_vermittlungscode(self, zip_code: str) -> str:
        """ Generiert Vermittlungscode via REST API Call """
        data = {
            'email': settings.MAIL,
            'leistungsmerkmal': 'L921',  # BioNTech, Moderna
            'phone': f'+49{settings.PHONE}',
            'plz': zip_code
        }

        r = self.s.post(f'{self.host}/rest/smspin/anforderung', json=data, timeout=25)

        if not r.json().get("token"):
            self.logger.error(f'An error occurred requesting code from server; response [{r.status_code}]')
            self.logger.info(r.text)

        return r.json().get("token")

    def verify_token(self, token: str, sms_pin: str) -> bool:
        """ Verifiziert Token via SMS PIN """
        data = {
            'token': token,
            'smspin': sms_pin
        }
        r = self.s.post(f'{self.host}/rest/smspin/verifikation', json=data, timeout=25)
        return r.status_code == 200