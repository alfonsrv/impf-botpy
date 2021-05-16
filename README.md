# Impf Bot.py 🐍⚡

[![Python](https://img.shields.io/badge/Made with-Python 3.x-blue.svg?style=flat-square&logo=Python&logoColor=white)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-3.141.59-green.svg?style=flat-square&logo=Selenium&logoColor=white)](https://www.selenium.dev/)

### Damit ihr im Sommer erstmal Entspahnen könnt ☀

Searches the official "[ImpfterminService - Der Patientenservice 116117](https://www.impfterminservice.de/)" for free
Corona vaccination slots. It can search multiple locations at once which can be provided in a list. 

When it finds a free slot, the bot sends you a notification message via Zulip (or any other platform/chat app). Just 
send your SMS confirmation code through your favorite chat app from anywhere and let your PC do the work while you're 
out and about.

Important timings can be configured to avoid being timed-out aka *shadow banned* (HTTP status code `429`).  

This is a Python implementation of the Java-based [💉🤖 Impf-Bot](https://github.com/TobseF/impf-bot)

## ⭐ Features
 ⭐ Easy to Set up  
 ⭐ Python for the 21st Century  
 ⭐ Full browser automation  
 ⭐ Concurrent checking  
 ⭐ Waiting room detection  
 ⭐ Timeout / Shadow Ban `429` detection  
 ⭐ Automatically re-checking *Vermittlungscode*  
 ⭐ `settings.py` for single point of configuration  
 ⭐ Zulip integration  
 ⭐ Run custom Commands for Alerting (Text-to-Speech preconfigured)  
 ⭐ Easy to add additional backends, like Telegram, Slack, Webhooks ...  

## Workflow

This is a two-step process. First you'll need a *Vermittlungscode* to then book a vaccination appointment. Each center
has its own valid *Vermittlungscode*, which you'll need to acquire first to advance to the next step.

1. If you do not have a *Vermittlungscode* for a center yet
    1. The bot will check the site to see if there is vacancy
    2. If there is vacancy, the bot will enter your age, email and phone number
    3. The bot will alert you that there is vacancy using the alert backends
    4. ImpfterminService will send you a SMS with a confirmation code
    5. Either enter the code manually or send it to the bot using `sms:123-456`
    6. The *Vermittlungscode* is sent to your email
    7. Enter the *Vermittlungscode* on the center in `settings.py` and restart the bot 🚨
2. If you have a *Vermittlungscode* for a center
    1. The bot will enter your *Vermittlungscode*
    2. It will check if there are available appointments
    3. If there are appointments, it will alert you using your alert backend
    4. You will have to manually choose the appointment for your best convenience
    5. Alternatively use a remote access tool (I prefer `AnyDesk`, but `TeamViewer` also works) 
       to access your machine remotely

The automatically opening browser windows can be run in the background.

> ### ⚠ Warning: The online booking isn't an authorization
> On the booking date you still have to bring the documents with you, to proof that you are qualified to receive the vaccination.
> Check out [the official guidelines](https://sozialministerium.baden-wuerttemberg.de/de/gesundheit-pflege/gesundheitsschutz/infektionsschutz-hygiene/informationen-zu-coronavirus/impfberechtigt-bw/)
> and make sure you are qualified for them. This bot doesn't help you get a privilege. It only allows you to get a date without losing the nerves or waisting a lifetime in pointless callcenter calls.

## Setup

### Requirements

* [Python 3.x](https://www.python.org/downloads/)
* [Selenium](https://www.selenium.dev) for Chrome
* Google Chrome
* `pip3 install -r requirements.txt`

### For Dummies

> I don't know anything about programming! And CLI gives me anxiety

Don't worry. It's easy. Follow [this](/INSTALL.md) Step-by-Step Guide and then come back.

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

1. Rename `settings.sample.py` to `settings.py`
2. Edit the `LOCATIONS` by adding your Impfzentrum with the name as shown on [ImpfterminService](https://impfterminservice.de/)
3. If you already have a *Vermittlungscode* for one of the centers, enter it at `code` - otherwise leave empty
4. Enter your age, mail and phone number

### Run it

`python3 main.py` und entspahnen

## Adding Backends for Alerts

Adding your favorite backend (e.g. Slack) for alerting is easy. Simply add your preferred integration to

1. `alert.py` and integrate it with `read_code()` and `send_alert()`
2. `constructor.py` if your API is a bit more complex to keep things tidy
3. `settings.py` add your relevant settings (must include `ENABLED` flag)
4. `main.py` in `print_config` for NextGen UX
4. Done 💥

