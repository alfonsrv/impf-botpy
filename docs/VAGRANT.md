# Vagrant Setup

Vagrant is an easy way to create a virtual machine with all the tools required for running impf-botpy.
The provided Vagrantfile takes care of installing Python, Python dependencies, Chromium and Selenium driver.

## Requirements

1. Download and install VirtualBox: https://www.virtualbox.org/wiki/Downloads
2. Download and install Vagrant: https://www.vagrantup.com/downloads
3. Install vagrant-vbguest plugin:
    ```bash
    vagrant plugin install vagrant-vbguest
    ```

## Setup

1. Clone this repository:
    ```bash
    git clone https://github.com/alfonsrv/impf-botpy.git
    ```
2. Configure your settings (see main [README.md](../README.md#Workflow) for details):
    ```bash
    cd impf-botpy
    # configure settings.py
    mv settings.sample.py settings.py
    ```

## Running the bot

1. Spin up the vagrant box:
    ```bash
    cd impf-botpy
    vagrant up
    vagrant reload
    ```
2. Start a terminal in the Vagrant box and run the bot:
    ```bash
    cd /app
    ./main.py
    ```
