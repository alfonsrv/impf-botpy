import json
from dataclasses import dataclass, field
from time import sleep, time
from typing import List, Tuple

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, \
    ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
from impf.alert import send_alert, read_backend

import logging

from impf.api import API
from impf.constructors import browser_options, format_appointments
from impf.decorators import shadow_ban, control_errors

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
        opts = browser_options()
        if settings.SELENIUM_PATH:
            self.driver = webdriver.Chrome(settings.SELENIUM_PATH, options=opts)
        else:
            self.driver = webdriver.Chrome(options=opts)
        self.driver.implicitly_wait(settings.WAIT_BROWSER_MAXIMUM // 4 or 2.5)
        self.wait = WebDriverWait(self.driver, settings.WAIT_BROWSER_MAXIMUM)
        self.logger = settings.LocationAdapter(logger, {'location': self.location[:5]})

    def reset(self, *args, **kwargs):
        """ Hacky Helper function to reset
        Browser instance while keeping data """
        self.driver.quit()
        self.__post_init__()
        self.error_counter = 0
        return self.control_main()

    def reinit(self, *args, **kwargs):
        """ Hacky Helper function to reinitialize
        Browser with new data - sorry """
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
    def server_id(self) -> str:
        """ Returns the server identifier we're connected to (001, 002, ...) """
        return self.driver.current_url[8:11]

    @property
    def has_vacancy(self) -> bool:
        """ Impfzentrum hat freie Termine """
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "alert-danger")]')))
            return not ('keine freien Termine' in element.text)
        except TimeoutException:
            return True

    @property
    def register_limit_reached(self) -> bool:
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
            return not ('Ungültiger Vermittlungscode' in element.text)
        except NoSuchElementException:
            return True

    @property
    def code_error(self) -> bool:
        """ Check ob Vermittlungscode an sich ok, aber auf Error gelaufen ist; bspw.
         wegen zu vielen Anfragen (429) """
        try:
            sleep(1.5)
            element = self.driver.find_element_by_xpath('//div[contains(@class, "kv-alert-danger")]')
            # interner Fehler x unerwarteter Fehler
            return 'Fehler' in element.text
        except NoSuchElementException:
            return False

    @property
    def code_booked(self) -> bool:
        """ Prüft ob Termin bereits gebucht wurde und wir auf Buchungsseite landen"""
        try:
            element = self.driver.find_element_by_xpath('//h2[contains(@class, "ets-booking-headline")]')
            return 'Ihr Termin' in element.text
        except NoSuchElementException:
            return False

    @property
    def code_expired(self) -> bool:
        """ Prüft ob Anspruch mit Vermittlungscode abgelaufen """
        try:
            element = self.driver.find_element_by_xpath('//div[contains(@class, "kv-alert-danger")]')
            return 'Anspruch abgelaufen' in element.text
        except NoSuchElementException:
            return False

    @property
    def loading_vacancy(self) -> bool:
        """ Prüft ob Verfügbarkeit noch geladen wird """
        try:
            element = self.driver.find_element_by_xpath('//div[contains(text(),"Bitte warten, wir suchen")]')
            return bool(element)
        except NoSuchElementException:
            return False

    @property
    def too_many_requests(self) -> bool:
        """ Checks if we're being blocked; unfortunately there is no better way, as
        Selenium doesn't allow us to check HTTP status codes in the Network tab """
        relevant = time() - 120
        sleep(1.5)  # give browser time to catch-up
        for log in self.driver.get_log('browser'):
            if log.get('level') == 'SEVERE' \
                    and log.get('source') == 'network' \
                    and (log.get('timestamp') / 1000) > relevant \
                    and '429' in log.get('message'):
                return True
        return False

    def cookie_popup(self) -> None:
        try:
            button = self.driver.find_element_by_xpath('//a[contains(text(), "Auswahl bestätigen")]')
            button.click()
        except:
            pass

    def inject_session(self) -> None:
        """ Sets Session Storage to allow Vermittlungcode request """
        d, m, y = settings.BIRTHDATE.split('.')
        birthday = f'{y}-{m}-{d}'
        storage = {"birthdate": birthday, "slotsAvailable": {"pair": True, "single": False}}
        payload = json.dumps(storage)
        self.logger.debug(f'sessionStorage.setItem("ets-session-its-cv-quick-check", "{payload}");')
        self.driver.execute_script(f'sessionStorage.setItem("ets-session-its-cv-quick-check", \'{payload}\');')

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
        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//li[@role="option" and contains(text() , "{settings.BUNDESLAND}")]')))
        element.click()
        self.logger.info(f'Selected Bundesland: {settings.BUNDESLAND}')

        # Load Cities
        elements[1].click()
        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//li[@role="option" and contains(text() , "{self.location}")]')))
        self.location_full = element.text
        element.click()
        self.logger.info(f'Selected Impfzentrum: {self.location_full}')

        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()
        sleep(.5)

    def waiting_room(self):
        if not self.in_waiting_room: return
        self.logger.info('Taking a seat in the waiting room (very german)')
        while self.in_waiting_room: sleep(5)
        self.logger.info('No longer in waiting room!')

    @shadow_ban
    def location_page(self) -> None:
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'Wurde Ihr Anspruch auf eine Corona-Schutzimpfung bereits geprüft?'
        self.cookie_popup()
        sleep(3)
        claim = 'Ja' if self.code else 'Nein'
        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             f'//input[@type="radio" and @name="vaccination-approval-checked"]//following-sibling::span[contains(text(),"{claim}")]/..')))

        # Small Mouse Wiggle heh
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()
        action.move_by_offset(40, 20).perform()
        sleep(.25)
        action.move_to_element(element).click().perform()
        action.move_by_offset(10, 5).perform()

        # Ensure vacancy has fully loaded before proceeding
        while self.loading_vacancy and claim == 'Nein':
            sleep(2.5)

    def confirm_eligible(self) -> None:
        """ Termin verfügbar; prüfe ob Termine für unser Alter """
        # TODO: Implement proper assertion
        #body = self.driver.find_element_by_tag_name('body')
        #assert 'Schnellprüfung durchführen' in body.text
        sleep(.5)
        element = self.wait.until(EC.presence_of_element_located(
            (By.XPATH,
             '//input[@type="radio" and @formcontrolname="isValid"]//following-sibling::span[contains(text(),"Ja")]/..')))
        element.click()

        # Enter Age
        input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@formcontrolname="birthdate"]')))
        input.send_keys(str(settings.BIRTHDATE))
        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    def claim_code(self) -> None:
        """ Alles ok! fülle Felder aus um Vermittlungscode via SMS zu erhalten """
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
        self.logger.warning('Enter SMS code! Waiting for user input.')
        send_alert(settings.ALERT_SMS.replace('{{ LOCATION }}', self.location_full))
        start = time()
        while (time() - start) < settings.WAIT_SMS_MANUAL:
            _code = read_backend('sms')
            if _code:
                self.logger.warning(f'Received Code from backend: {_code} - entering now...')
                send_alert(f'Entering code "{_code}"; check your mails!  \n'
                           f'Thanks for using RAUSYS Technologies :)')
                return _code
            sleep(15)
        self.logger.warning('No SMS code received from backend')

    def alert_appointment(self) -> None:
        """ Benachrichtigung User - um entweder Termin via ext. Plattform (Zulip, ...) zu buchen
        oder manuell einzugeben. Kritischste Funktion – max. Exception-Verschachtelung """
        self.logger.warning('Available appointments! Waiting for user input')
        alert = settings.ALERT_AVAILABLE\
            .replace('{{ LOCATION }}', self.location_full)\
            .replace('{{ LINK }}', self.driver.current_url)
        send_alert(alert)
        self.keep_browser = True

        if not settings.BOOK_REMOTELY:
            self.logger.warning('Exiting in 10 minutes, our job here is done. Keeping browser open.')
            return

        try:
            self.remote_booking()
        except:
            self.logger.exception('Unexpected exception occurred trying to book appointments remotely!')
            send_alert('Appointment could not be booked – please continue manually!')

    def remote_booking(self) -> None:
        """ Hilfsfunktion um Termine Remote zu buchen – wartet auf max 10 Minuten
        auf User Input via Chat App und fährt dann fährt dann fort """
        # Booking remotely - should probably be a dedicated function
        api = API(driver=self)
        appointments = api.control_appointments()

        if not appointments:
            self.logger.warning('BOOK_REMOTELY enabled, but appointments empty! Please continue manually')
            send_alert('Booking remotely enabled, but didn\'t get appointments from backend. Please continue manually!')
            return

        fappointments = format_appointments(appointments.get('termine'))
        send_alert(settings.ALERT_BOOKINGS.replace('{{ APPOINTMENTS }}', '  \n'.join(fappointments)))

        start = time()
        while (time() - start) < settings.WAIT_SMS_MANUAL:
            _code = read_backend('appt')
            if _code:
                self.logger.warning(f'Received Appointment indicator from backend: {_code} - booking now...')
                if api.book_appointment(appointments, int(_code)) or self.book_appointment(int(_code)):
                    appointment = fappointments[int(_code) - 1].replace("* ", "").replace(f' (appt:{_code})', '')
                    send_alert(f'Successfully booked appointment "**{appointment}**" – check your mails!  \n'
                               f'Thanks for using RAUSYS Technologies :)  \n'
                               f'Feedback is highly appreciated: '
                               f'https://github.com/alfonsrv/impf-botpy/issues/1 and only takes 2 seconds!')
                    self.logger.info('Booking confirmed! Feedback is highly appreciated: '
                                     'https://github.com/alfonsrv/impf-botpy/issues/1 and only takes 2 seconds!')
                    return
                raise Exception('Did not get <201 Created> from server')
            sleep(15)

        self.logger.warning('No Appointment indicator received from backend')

    @shadow_ban
    def fill_code(self) -> None:
        """ Vermittlungscode für Location eingeben und prüfen """
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'Wurde Ihr Anspruch auf eine Corona-Schutzimpfung bereits geprüft?'
        for i in range(3):
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, f'//input[@type="text" and @data-index="{i}"]')))
            code = self.code.split('-')[i]
            element.clear()
            element.send_keys(code)

        submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit"]')))
        submit.click()

    @shadow_ban
    def search_appointments(self) -> bool:
        """ Suche Termine mit Vermittlungscode """
        title = self.wait.until(EC.presence_of_element_located((By.XPATH, '//h1')))
        assert title.text == 'Onlinebuchung für Ihre Corona-Schutzimpfung'

        try:
            close = self.driver.find_elements_by_xpath('//button[contains(text(), "Abbrechen")]')[-1]
            close.click()
            sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
            self.logger.debug('Could not find "Abbrechen" button - this usually happens when you are running in a slow '
                              'environment such as Docker or if the ImpfterminService site has changed.')

        try:
            submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Termine suchen")]')))
            submit.click()
            sleep(2.5)

        # Docker seems to have consistent runtime errors
        except ElementClickInterceptedException:
            self.logger.info('Could not click "Termine suchen" button - this usually happens when you are running in a slow '
                             'environment such as Docker or if the ImpfterminService site has changed.')
            return self.search_appointments()

        try:
            if self.driver.find_element_by_xpath('//span[@class="its-slot-pair-search-no-results"]') \
                    or self.driver.find_element_by_xpath(
                    '//span[contains(@class, "text-pre-wrap") and contains(text(), "Fehler")]'):
                self.logger.info('Vermittlungscode ok, but not free vaccination slots')
                return False
        except NoSuchElementException:
            pass

        # Fallback is internet connection too slow in order to avoid crash
        try: element = self.driver.find_element_by_xpath('//*[contains(text(), "1. Impftermin")]')
        except NoSuchElementException: element = None
        return bool(element)

    def book_appointment(self, appointment: int) -> bool:
        """ Bucht Termin <appointment> via Browser mit den in settings.py spezifizierten
        personenbezogenen Daten – Funktion dient als Fallback (shoutout github/timoknapp) """

        # Step 1 – Select Appointment
        elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//input[@type="radio" and @formcontrolname="slotPair"]//following-sibling::div[contains(@class,"its-slot-pair-search-slot-wrapper")]/..')))
        # Select appointment ID user submitted via backend
        elements[appointment-1].click()

        try:
            submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit" and contains(text(), "AUSWÄHLEN")]')))
            submit.click()
        except:
            # Button not clickable – timer likely expired due to racing condition; attempting to recover automatically
            self.search_appointments()
            return self.book_appointment()

        # Step 2 – Input Data
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//button[contains(text(), "Daten erfassen")]')))
        element.click()

        salutation = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//input[@type="radio" and @name="salutation"]//following-sibling::span[contains(text(), "{settings.SALUTATION}")]/..')))
        salutation.click()

        enter_form = lambda elem, id: self.wait.until(EC.presence_of_element_located((By.XPATH, f'//input[@formcontrolname="{elem}"]'))).send_keys(getattr(settings, id))
        enter_form('firstname', 'FIRST_NAME')
        enter_form('lastname', 'LAST_NAME')
        enter_form('zip', 'ZIP_CODE')
        enter_form('city', 'CITY')
        enter_form('street', 'STREET_NAME')
        enter_form('housenumber', 'HOUSE_NUMBER')
        enter_form('phone', 'PHONE')
        enter_form('notificationReceiver', 'MAIL')

        try:
            submit = self.wait.until(EC.element_to_be_clickable((By.XPATH, f'//button[@type="submit" and contains(text(), "Übernehmen")]')))
            submit.click()
        except:
            # Button not clickable – timer likely expired due to racing condition; attempting to recover automatically
            self.search_appointments()
            return self.book_appointment()

        # Step 3 – Leben zurückbekommen
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, f'//button[contains(text(), "VERBINDLICH BUCHEN")]')))
        element.click()

        return self.code_booked


    def wiggle_recover(self) -> None:
        """ Can solve `429` error by clicking Yes, No """
        claims = [
            'Nein' if self.code else 'Ja',  # click opposite than current
            'Ja' if self.code else 'Nein'
        ]
        for claim in claims:
            element = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, f'//input[@type="radio" and @name="vaccination-approval-checked"]//following-sibling::span[contains(text(),"{claim}")]/..')))
            element.click()
            sleep(2)


    @control_errors
    def control_main(self):
        """ 1/2 Kontrollfunktion um Vermittlungscode zu beziehen """
        if self.error_counter == 5:
            self.logger.error('Maximum errors and retries exceeded - skipping location for now')
            return

        # Quick Restart
        if self.error_counter == 0: self.main_page()
        else: self.driver.refresh()

        self.logger.info(f'Connected to server [{self.server_id}]')
        self.waiting_room()
        self.location_page()
        if self.code: return self.control_vermittlungscode()
        if not self.has_vacancy: self.logger.info('No vacancy right now...'); return
        self.confirm_eligible()
        if not self.has_vacancy: self.logger.info('No vacancy right now...'); return
        return self.control_sms()

    @control_errors
    def control_sms(self) -> None:
        """ 2/2 Kontrollfunktion um Vermittlungscode zu beziehen """
        self.logger.warning(f'We have vacancy! Requesting Vermittlungscode for {self.driver.current_url}')
        self.claim_code()
        if self.register_limit_reached:
            self.logger.error('Request limit reached - try using a different phone number and email')
            send_alert(f'Server [{self.server_id}] returned max. requests. Consider changing phone number and email')
            return
        sms_code = self.alert_sms()
        self.enter_sms(sms_code)
        self.logger.info('Add the code you got via mail to settings.py and restart the script!')

    @control_errors
    def control_vermittlungscode(self):
        """ 1/2 Kontrollfunktion gibt Vermittlungscode ein - um Verfügbarkeit
        von Impfterminen mit vorhandenem Vermittlungscode zu prüfen """
        self.fill_code()

        if self.code_error:
            # We're likely sending too many requests too quickly or the server is under too much stress
            self.logger.info(
                f'Ran into what is probably a temporary error with code {self.code}; retrying in '
                f'{settings.WAIT_SHADOW_BAN // 60}min')
            sleep(settings.WAIT_SHADOW_BAN)
            self.error_counter += 3
            return self.control_main()

        code_reason = ''
        if not self.code_valid: code_reason = f'invalid for server [{self.server_id}]'
        if self.code_booked: code_reason = 'already used'
        if self.code_expired: code_reason = 'has expired'

        if code_reason:
            self.logger.warning(f'Vermittlungscode "{self.code}" {code_reason}!')
            self.logger.info('Removing code from global config for current runtime and continuing without it')
            self.code = ''
            return self.control_main

        self.control_appointment()

    @control_errors
    def control_appointment(self) -> None:
        """ 2/2 Kontrollfunktion sucht nach Terminen - um Verfügbarkeit von
        Impfterminen mit vorhandenem Vermittlungscode zu prüfen """

        appointments = self.search_appointments()
        if settings.RESCAN_APPOINTMENT and not appointments:
            self.logger.info(f'RESCAN_APPOINTMENT is enabled - automatically rechecking in '
                             f'{settings.WAIT_RESCAN_APPOINTMENTS // 60}min...')
            while not appointments:
                sleep(settings.WAIT_RESCAN_APPOINTMENTS)
                self.logger.info('Rechecking for new appointments')
                appointments = self.search_appointments()

        if appointments:
            self.alert_appointment()
            sleep(600)
            exit()
        if settings.RESCAN_APPOINTMENT: return self.control_appointment()
        # Rescanning for appointments not enabled
        self.logger.info('No appointments available right now :(')


    def control_assert(self):
        """ Hilfsfunktion - wenn ein AssertionError auftritt (Titel stimmt nicht mit aktuellem
        Funktionsabruf überein) fährt der Bot mit dem entsprechenden Workflow für wesentliche
        Schlüsselseiten (Terminbuchung, SMS Bestätigung, ...) fort.
        Das ermöglicht es dem User außerdem frei auf der Seite zu navigieren, ohne den Bot
        zum Absturz zu führen und autom. an der aktuellen Stelle fortzufahren """
        title = self.driver.find_element_by_xpath('//h1')
        self.logger.info(f'Current page title is "{title}"')

        if title.text == 'Wurde Ihr Anspruch auf eine Corona-Schutzimpfung bereits geprüft?' and self.code:
            self.logger.info('Continuing with <control_vermuttlingscode>')
            self.location_page()
            return self.control_vermittlungscode()

        if title.text == 'Vermittlungscode anfordern':
            self.logger.info('Continuing with <control_sms>')
            return self.control_sms()

        if title.text == 'Onlinebuchung für Ihre Corona-Schutzimpfung':
            self.logger.info('Continuing with <control_appointment>')
            return self.control_appointment()

        if title.text == 'Buchen Sie die Termine für Ihre Corona-Schutzimpfung':
            self.error_counter = 0

        # Virtueller Warteraum des Impfterminservice
        # SMS Verifizierung
        self.logger.info('Continuing with reset via <control_main>')
        self.error_counter = 1
        return self.control_main()
