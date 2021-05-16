from dataclasses import dataclass, field
from time import sleep, time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
from impf.alert import send_alert, read_code

import logging
logger = logging.getLogger(__name__)

@dataclass
class Browser:
    driver: webdriver = field(init=False)
    wait: WebDriverWait = field(init=False)
    location: str
    code: str = ''
    location_full: str = ''  # Helper variable for extracting full MVZ name
    keep_browser: bool = False  # Helper variable to indicate whether or not to keep browser open for reuse
    error_counter: int = 0  # Helper variable to avoid infinite loop
    logger: logger = field(init=False)  # Internal adapter-logger to add PLZ field

    def __post_init__(self):
        opts = Options()
        if settings.SELENIUM_DEBUG: opts.add_argument('--auto-open-devtools-for-tabs')
        if settings.USER_AGENT != 'default': opts.add_argument(f'user-agent={settings.USER_AGENT}')
        if settings.SELENIUM_PATH: self.driver = webdriver.Chrome(settings.SELENIUM_PATH, chrome_options=opts)
        else: self.driver = webdriver.Chrome(chrome_options=opts)
        self.driver.implicitly_wait(2.5)
        self.wait = WebDriverWait(self.driver, settings.WAIT_BROWSER_MAXIMUM)
        self.logger = settings.LocationAdapter(logger, {'location': self.location[:5]})

    def reinit(self, *args, **kwargs):
        """ Hacky Helper function - sorry """
        self.location = kwargs.get('location')
        self.code = kwargs.get('code')
        self.error_counter = 0
        self.location_full = ''
        self.logger = settings.LocationAdapter(logger, {'location': self.location[:5]})

    @property
    def in_waiting_room(self) -> bool:
        """ Momentan im Warteraum? """
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        return title.text == 'Virtueller Warteraum des Impfterminservice'

    @property
    def has_vacancy(self) -> bool:
        """ Impfzentrum hat freie Termine """
        try:
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "alert-danger")]')))
            return not('keine freien Termine' in element.text)
        except TimeoutException:
            return True

    @property
    def limit_reached(self) -> bool:
        """ Max. Anzahl an Nummern-Registrierungen erreicht """
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Anfragelimit erreicht")]')))
            return bool(element)
        except TimeoutException:
            return False

    @property
    def code_valid(self) -> bool:
        """ Check ob Vermittlungscode von Server generell akzeptiert wird """
        try:
            element = self.driver.find_element_by_xpath('//div[contains(@class, "kv-alert-danger")]')
            return not('Ungültiger Vermittlungscode' in element.text)
        except NoSuchElementException:
            return True

    @property
    def code_error(self) -> bool:
        """ Check ob Vermittlungscode an sich ok, aber auf Error gelaufen ist; bspw.
         wegen zu vielen Anfragen (429) """
        try:
            element = self.driver.find_element_by_xpath('//div[contains(@class, "kv-alert-danger")]')
            return 'unerwarteter Fehler' in element.text
        except NoSuchElementException:
            return False

    @property
    def loading_vacancy(self):
        """ Prüft ob Verfügbarkeit noch geladen wird """
        try:
            element = self.driver.find_element_by_xpath('//div[contains(text(),"Bitte warten, wir suchen")]')
            return bool(element)
        except NoSuchElementException:
            return False


    def cookie_popup(self) -> None:
        try:
            button = self.driver.find_element_by_xpath('//a[contains(text(),"Auswahl bestätigen")]')
            button.click()
        except:
            pass

    def page_ready(self) -> bool:
        """ Not in use; optional to check if page is ready (unreliable) before proceeding """
        page_state = self.driver.execute_script('return document.readyState;')
        return page_state == 'complete'

    def main_page(self) -> None:
        self.logger.info('Navigating to ImpfterminService')
        self.driver.get('https://www.impfterminservice.de/impftermine')
        elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@role="combobox"]')))
        title = self.driver.find_element_by_xpath('//h1')
        assert title.text == 'Buchen Sie die Termine für Ihre Corona-Schutzimpfung'
        self.cookie_popup()

        # Load Bundesländer
        elements[0].click()
        # Select BaWü
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//li[@role="option" and contains(text() , "{settings.BUNDESLAND}")]')))
        element.click()
        self.logger.info(f'Selected Bundesland: {settings.BUNDESLAND}')

        # Load Cities
        elements[1].click()
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//li[@role="option" and contains(text() , "{self.location}")]')))
        self.location_full = element.text
        element.click()
        self.logger.info(f'Selected Impfzentrum: {self.location_full}')

        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    def waiting_room(self):
        if not self.in_waiting_room: return
        self.logger.info('Taking a seat in the waiting room (very german)')
        while self.in_waiting_room: sleep(5)
        self.logger.info('No longer in waiting room!')

    def location_page(self) -> None:
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'Wurde Ihr Anspruch auf eine Corona-Schutzimpfung bereits geprüft?'
        self.cookie_popup()
        claim = 'Ja' if self.code else 'Nein'
        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//input[@type="radio" and @name="vaccination-approval-checked"]//following-sibling::span[contains(text(),"{claim}")]/..')))
        element.click()

    def confirm_eligible(self) -> None:
        """ Termin verfügbar; prüfe ob Termine für unser Alter """
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()
        sleep(.5)
        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//input[@type="radio" and @formcontrolname="isValid"]//following-sibling::span[contains(text(),"Ja")]/..')))
        element.click()

        # Enter Age
        input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@formcontrolname="age"]')))
        input.send_keys(str(settings.AGE))
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    def claim_code(self) -> None:
        """ Alles ok! fülle Felder aus um Vermittlungscode zu erhalten """
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'Vermittlungscode anfordern'
        mail = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@formcontrolname="email"]')))
        mail.send_keys(settings.MAIL)
        phone = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@formcontrolname="phone"]')))
        phone.send_keys(settings.PHONE)
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    def enter_sms(self, sms_code: str) -> None:
        """ Gibt den SMS Code ins Formular ein """
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'SMS Verifizierung'
        code = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@formcontrolname="pin"]')))
        code.send_keys(sms_code)
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    def alert_sms(self) -> str:
        """ Benachrichtigung User - um entweder SMS Code via ext. Plattform (Zulip, ...)
        oder manuell einzugeben. Wartet max. 10 Minuten, und fährt dann fährt dann fort """
        self.logger.info('Enter SMS code!')
        send_alert(settings.ALERT_TEXT.replace('{{ LOCATION }}', self.location_full))
        start = time()
        while (time() - start) < settings.WAIT_SMS_MANUAL:
            _code = read_code()
            if _code:
                send_alert('Entering code; check your mails! Thanks for using RVX Technologies :)')
                return _code
            sleep(15)
        self.logger.info('No SMS code received from backend; exiting'); exit()

    def fill_code(self) -> None:
        """ Vermittlungscode für Location eingeben und prüfen """
        for i in range(3):
            element = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//input[@type="text" and @data-index="{i}"]')))
            element.send_keys(self.code.split('-')[i])
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    def search_appointments(self) -> bool:
        """ Suche Termine mit Vermittlungscode """
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[contains(text(),"Termine suchen")]')))
        submit.click()
        sleep(2.5)
        if self.driver.find_element_by_xpath('//span[@class="its-slot-pair-search-no-results"]') \
            or self.driver.find_element_by_xpath('//span[contains(@class, "text-pre-wrap") and contains(text(), "Fehler")]'):
            self.logger.info('Vermittlungscode ok, but not free vaccination slots')
            return False

        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'Onlinebuchung für Ihre Corona-Schutzimpfung'
        element = self.driver.find_element_by_xpath('//*[contains(text(), "1. Impftermin")]"')
        return bool(element)

    def alert_available(self):
        """ Alerts ... """
        self.logger.info('Available appointments!')
        send_alert(f'Appointments available at {self.location_full}! Reserved for the next 10 minutes...')
        sleep(600)

    def control_main(self):
        """ Kontrollfunktion um Vermittlungscode zu beziehen """
        try:
            if self.error_counter == 3:
                self.logger.error('Maximum errors exceeded...')
                return
            self.main_page()
            self.waiting_room()
            self.location_page()
            if self.code: return self.control_appointment()

            while self.loading_vacancy: sleep(2.5)
            if not self.has_vacancy: self.logger.info('No vacancy right now...'); return
            self.confirm_eligible()
            if not self.has_vacancy: self.logger.info('No vacancy right now...'); return
            self.logger.info('We have vacancy! Requesting Vermittlungscode')
            self.claim_code()
            if self.limit_reached: self.logger.info('Request limit reached'); return
            sms_code = self.alert_sms()
            self.enter_sms(sms_code)
            self.logger.info('Add the code you got via mail to settings.py and restart the script!')
        except:
            raise
        finally:
            if not self.keep_browser: self.driver.close()

    def control_appointment(self):
        """ Kontrollfunktion um Verfügbarkeit von Impfterminen
         mit vorhandenem Vermittlungscode zu prüfen """
        self.fill_code()
        if not self.code_valid:
            self.logger.info(f'Code invalid for server {self.driver.current_url}')
            self.code = ''
            return self.control_main()
        if self.code_error:
            # We're likely sending too many requests too quickly
            self.logger.info(f'Ran into what is probably a temporary error with code {self.code}; retrying in a bit')
            sleep(900)
            self.error_counter += 1
            return self.control_main()
        x = self.search_appointments()
        if x: self.alert_available()
        else: self.logger.info('No appointments available right now :(')
