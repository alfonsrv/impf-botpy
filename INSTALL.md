# Installation Guide

This guide is designed to be as easy as possible. If anything is unclear, please feel free to ask.

## Windows

Make sure you have Google Chrome installed.

### Selenium Installation

Open Command Line (`Windows` -> Start typing to activate search `cmd` -> `Rightclick` -> `Run as Administrator`)

```shell
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
choco install selenium-chrome-driver
```

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

----


## macOS

Make sure you have Google Chrome installed.

### Selenium macOS

Open `Terminal` and Copy+Paste the code below:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install selenium-server-standalone
```

It will ask for your password. Just type it and press Enter. You won't be able to see it, so don't get confused.

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
pip3 install -r requirements.txt
python3 main.py
```

---

## Debian / Ubuntu / Rapsberry Pi

Make sure you have Google Chrome installed.

### Selenium

```bash
sudo apt update && sudo apt install chromium-chromedriver -y
```

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