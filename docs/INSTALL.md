# Installation Guide

This guide is designed to be as easy as possible. If anything is unclear, please feel free to ask. Every OS has its own
subchapter - be sure you follow the steps for your system.

## Windows

Make sure you have Google Chrome installed.

### Selenium Installation

1. Open your Chrome Browser 
2. Click on the three dots (top right) to expand the settings
3. Help -> About Google Chrome
4. Note the Version (89.0..., 90.0..., 91.0...)
5. Visit the [Selenium WebDriver website](https://sites.google.com/a/chromium.org/chromedriver/downloads)
6. Download the zip-Archive
7. Put the `chromedriver.exe` from the zip-Archive in the `impf-botpy` folder after downloading the project (further down) – alternatively you can:
  * put it into `C:\Windows` straight away or if you're experiencing issues
  * put it somewhere else, but you should make sure the folder is in your %PATH%-variable
  * point the `SELENIUM_PATH` in `settings.py` to the path of the `chromedriver.exe` explicitly
8. If you configured this step improperly, the bot will fail with this error - or a similar one
   `selenium.common.exceptions.WebDriverException: Message: 'chromedriver.exe' executable needs to be in PATH. Please see https://sites.google.com/a/chromium.org/chromedriver/home`
   OR `WebDriverException: unknown error: cannot find Chrome binary error with Selenium in Python for older versions of Google Chrome`

### Python Installation

Download Python: https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
When installing Python make sure to click `Customize Installation` and check
* Install for all Users
* Add Python to environment variables
* Precompile standard library

### Download Project

Download the Project. To do that go to the main site, click `Code` (green button top right) -> `Download ZIP`

Extract the ZIP file. Configure the project `settings.py` as shown in `README.md` and then type in Temrinal:

Open Command Line again. And type the following

```bash
cd Downloads/impf-botpy-main
pip3 install -r requirements.txt --user
python3 main.py
```

If it gives you an error, simply type `cd ` and Drag+Drop the extracted folder with the `main.py` in the Command Line window.
Press Enter and continue with the `pip3`-Step

If you get an error regarding `cryptography` and `Rust`, simply open the `requirements.txt` and remove the lines 
starting with `cryptography` + `zulip` and run `pip` again.

### Troubleshooting

* Error: `WebDriverException: unknown error: cannot find Chrome binary error with Selenium in Python for older versions of Google Chrome`
  * Copy the path of your chrome.exe file (e.g. `C:\Program Files\Google\Chrome\Application\chrome.exe`) and set it as `CHROME_PATH` in `settings.py`
* Error: `Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.`
  * Try running `python main.py` instead. If that doesn't work, see below.
  * You did not install Python properly. Either reinstall, following the steps or delete the `python.exe` and `python3.exe` in `%LocalAppData%\Microsoft\WindowsApps`
----

## macOS

Make sure you have Google Chrome installed.

### Selenium macOS

#### Option 1

Open `Terminal` and Copy+Paste the code below:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install chromedriver
xattr -dr com.apple.quarantine /usr/local/bin/chromedriver
```

It will ask for your password. Just type it and press Enter. You won't be able to see it, so don't get confused.

#### Option 2

Alternatively, you can download the executable here manually `https://sites.google.com/a/chromium.org/chromedriver/downloads`
See the Selenium installation for Windows for more details regarding which version to pick.

Move the `chromedriver` from the zip-archive to `/usr/local/bin` and then run `export PATH=$PATH:/usr/local/bin` for
good measure in Terminal.

### Python Installation

Open `Terminal` and type

```bash
brew install python3 git
curl https://bootstrap.pypa.io/get-pip.py | python3
```

### Download Project

Open `Terminal` and type

```bash
cd ~/Downloads/
git clone https://github.com/alfonsrv/impf-botpy.git
```

Configure the project `settings.py` as shown in `README.md` and then type in Temrinal:

```bash
cd ~/Downloads/impf-botpy
python3 -m pip install -r requirements.txt --user
python3 main.py
```


---

## Debian / Ubuntu / Rapsberry Pi

Make sure you have Google Chrome installed.

### Selenium

```bash
sudo apt update && sudo apt install chromium-chromedriver -y
```

Alternatively, you can download the executable here manually `https://sites.google.com/a/chromium.org/chromedriver/downloads`

### Python Installation

```bash
sudo apt install python3 python3-pip git
```

### Download Project

Open `Terminal` and type

```bash
cd ~/Downloads/
git clone https://github.com/alfonsrv/impf-botpy.git
```

Configure the project `settings.py` as shown in `README.md` and then type in Temrinal:

```bash
cd ~/Downloads/impf-botpy
pip3 install -r requirements.txt
python3 main.py
```
