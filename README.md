# Impf Bot.py 🐍⚡ – Bot für Impftermine

[![Python](https://img.shields.io/badge/Made%20with-Python%203.x-blue.svg?style=flat-square&logo=Python&logoColor=white)](https://www.python.org/) 
[![Selenium](https://img.shields.io/badge/Selenium-3.141.0-green.svg?style=flat-square&logo=Selenium&logoColor=white)](https://www.selenium.dev/) 
[![Version](https://img.shields.io/badge/Version-0.47-dc2f02.svg?style=flat-square&logoColor=white)](https://github.com/alfonsrv/impf-botpy)

### Entspahnt in den Sommer ☀

Automatisierte Impftermin-Vermittlung des offiziellen [ImpfterminService - Der Patientenservice 116117](https://www.impfterminservice.de). 
Der Bot kann mehrere Standorte parallel durchsuchen und auf verfügbare Terminen überwachen. Dabei wird der gesamte 
Prozess von der Vermittlungscode-Beschaffung bis zur Reservierung und Benachrichtigung freier Termine ganzheitlich 
abgebildet.

Wenn ein freier Impftermin / Slot gefunden wird, sendet der Bot eine Benachrichtigung via Zulip, Telegram oder Pushover 
(Slack, Webhooks, ... sind einfach integrierbar) und macht den Benutzer via Sprachausgabe auf den Slot aufmerksam. 
So kann der SMS Bestätigungscode manuell oder von überall unterwegs via Lieblings-Chat App übermittelt werden - 
Impf Bot.py erledigt den Rest. - [detaillierter Workflow](#Workflow)

Der Bot verwendet Browser-Automatisierung, die im Hintergrund laufen kann und es dem Benutzer ermöglicht manuell 
einzugreifen sowie einfach nachzuvollziehen, was gerade passiert. Die wichtigen Timings können dabei eingestellt
werden, um einen Timeout (bzw. *Shadow Ban*) zu vermeiden.

This is an improved Python implementation of the Java-based [💉🤖 Impf-Bot](https://github.com/TobseF/impf-bot) which
did a lot of the heavy lifting.

## ⭐ Features
 ⭐ Easy to set up  
 ⭐ Book appointments remotely  
 ⭐ Python for the 21st Century  
 ⭐ Full browser automation   
 ⭐ Concurrent checking  
 ⭐ Waiting room detection  
 ⭐ Instant Vermittlungscode Creation  
 ⭐ Timeout / Shadow Ban `429` detection  
 ⭐ Automatically re-check *Vermittlungscode*  
 ⭐ `settings.py` for single point of configuration  
 ⭐ Manual user intervention & smart error resilience  
 ⭐ Zulip, Pushover, Telegram integration  
 ⭐ Run custom Commands for Alerting (Text-to-Speech preconfigured)  
 ⭐ Easy to add additional backends, like Slack, Webhooks ...  
 ⭐ Docker Support  

## Workflow

This is a two-step process. First you'll need a *Vermittlungscode* to then book a vaccination appointment. Each center<sup>*</sup>
has its own valid *Vermittlungscode*, which you'll need to acquire first to advance to the next step.

1. If you do not have a *Vermittlungscode* for a center yet - you can either follow the standard
   workflow described below or create one instantly (see [Run it](#Run-it-))
    * The bot will check the site to see if there is vacancy
    * If there is vacancy, the bot will enter your age, email and phone number
    * The bot will alert you that there is vacancy using the alert backends
    * ImpfterminService will send you a SMS with a confirmation code
    * Either enter the code manually or send it to the bot using `sms:123-456`
    * The *Vermittlungscode* is sent to your email
    * Enter the *Vermittlungscode* on the center in `settings.py` and restart the bot 🚨
2. If you have a *Vermittlungscode* for a center
    * The bot will enter your *Vermittlungscode*
    * It will check if there are available appointments
    * If there are appointments, it will alert you using your alert backend
    * You can choose an appointment using your favorite chat app `appt:1` or book the appointment manually
    * To book an appointment manually when you're not on your PC, use a remote access tool (I prefer `AnyDesk`, but 
      `TeamViewer` also works) to access your machine remotely

<sup>* Every center is hosted on a server, indicated by the numbers in the URL, e.g. 
https://001-iz.impfterminservice.de/impftermine/service?plz=70713 is server **001**.
Vermittlungscodes are valid for *every* center on the given server 
[ref](https://www.impfterminservice.de/assets/static/impfzentren.json)</sup>  


> ### ⚠ Warning: The online booking isn't an authorization
> On the booking date you still have to bring the documents with you, to proof that you are qualified to receive the vaccination.
> Check out [the official guidelines](https://sozialministerium.baden-wuerttemberg.de/de/gesundheit-pflege/gesundheitsschutz/infektionsschutz-hygiene/informationen-zu-coronavirus/impfberechtigt-bw/)
> and make sure you are qualified for them. This bot doesn't help you get a privilege. It only allows you to get a date without losing the nerves or waisting a lifetime in pointless callcenter calls.

## Setup 👾

### Requirements

* [Python 3.x](https://www.python.org/downloads/)
* [Selenium](https://sites.google.com/a/chromium.org/chromedriver/downloads) for Chrome
* Google Chrome
* `pip3 install -r requirements.txt`

### For Dummies

> I don't know anything about programming! And CLI gives me anxiety

Don't worry. It's easy. Follow [this](/docs/INSTALL.md) Step-by-Step Guide and then come back.

### For Techies

```bash
git clone https://github.com/alfonsrv/impf-botpy.git
cd impf-botpy
pip3 install -r requirements.txt
# configure settings.py
mv settings.sample.py settings.py
python3 main.py
```

### Configuration

1. Rename `settings.sample.py` to `settings.py` and open it with your favorite text editor (recommended: Sublime Text)
2. Edit the `LOCATIONS` by adding your Impfzentrum with the name as shown on [ImpfterminService](https://impfterminservice.de/)
3. If you already have a *Vermittlungscode* for one of the centers, enter it at `code` - otherwise leave empty
4. Enter your age, mail and phone number
5. The rest of the settings is ok as is. If you want to check locations with multiple browsers at the same time, dig 
into the `Advanced Features` section.

### Alerting

Audio alerting is already preconfigured. If you also want to use smartphone notifications in order to interact with 
the bot remotely, follow [this](/docs/ALERTS.md) setup guide.

### Run it ⚡ 

* `python3 main.py` und entspahnen
* `python3 main.py --alerts` to test configured alerts
* `python3 main.py --code` to instantly create a *Vermittlungscode* (works best from 23:00 to 07:00)

### Docker

Please refer to the [Docker Setup](/docs/DOCKER.md) to run on a headless server.

## Support & Contributing 🪢

### Feature Requests & Feedback

Stuck? Too complex? File an [issue](https://github.com/alfonsrv/impf-botpy/issues/new/choose)!

Successfully booked an appointment?  
Feedback and feature requests are always much appreciated and can be submitted 
[here](https://github.com/alfonsrv/impf-botpy/issues/1)!

### Web Designers

If you're a web designer and want to create a [GitHub Pages](https://pages.github.com/) for this project, you're 
more than welcome!

### Adding Backends for Alerts

Contributions are welcome! Adding your favorite backend (e.g. Slack) for alerting is easy. 
Simply add your preferred integration to

1. `alert.py` and integrate it with `read_backend()` and `send_alert()`
2. `constructor.py` if your API is a bit more complex to keep things tidy
3. `settings.py` add your relevant settings (must include `ENABLED` flag)
4. `main.py` in `print_config` for NextGen UX
5. Optional: Setup Guide in [ALERTS.md](/docs/ALERTS.md)
6. Pull Request & Done 💥

### Unit Tests

Good with pyTest? Help this project creating some proper test coverage! Unfortunately I'm pretty unexperienced with 
mocking requests and what good tests should look like. Even just a few are enough, so I can get the hang of it.

### Stay Up-to-Date

⚠ **Please note:** Even though this bot is geared towards being as solid as possible, you should consider regularly 
checking this repository (site) to ensure you have the latest version. Unfortunately this is a bit of an arms 
race as the website is under constant modification. Checking the version at the top of the page and comparing it with 
`python main.py --version` is usually quite a good way to see if you're up-to-date. Alternatively you can get 
`Notifications` on top of the page to know whenever the code changes.  
When updating especially ensure your `settings.py` has all the options!

---

<br/>

Auch ich wünschte, dass es so n Tool nicht geben müsste, aber ist aktuell einfach absolute Katastrophe. Seid vernünftig 
und missbraucht den Bot nicht, ja?

[![Buy me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/alfonsrv)  

[![Ärzte ohne Grenzen](https://www.aerzte-ohne-grenzen.de/sites/germany/themes/msf_germany/img/logos/msf_germany_logo.png)](https://ssl.aerzte-ohne-grenzen.de/form/onlinespende-einmalig)