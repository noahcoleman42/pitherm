This is an rpi thermostat code.

Ideally, this will be simple and stupid.

I've implemented a really dumb Flask web controlling interface. This should be prettified and made mobile friendly.

There are a lot of SD card corruption issues when using this long-term. I should put the OS and the thermostat code on a read-only partition.

# Installation
## Circuit
I used a Pi Zero W for this, but really any Pi with an internet connection should work.

First, you'll need to connect your Pi to your MCP9808 and relays.
Links to purchased ones.
My circuit is:
![diagram](https://raw.githubusercontent.com/rjrosati/pitherm/master/schematic.png)
The Pi can't sink enough current to turn on the relays, so we use the Pi to turn on transistors and switch the relays from USB power. Note the pull-up resistors.

Note: many AC units don't automatically turn on the fan. Mine didn't, so I shorted white to green.

## Software
You should install the latest raspbian-lite and set up your Pi to connect to your network on boot.

Then you can install the software:

    sudo apt update
    sudo apt upgrade
    sudo apt install git virtualenv tmux python3-dev ntp

Let those install, then run `raspi-config` and do the following:
* set your time zone
* enable the I2C interface

Reboot, then you should be able to install `pitherm`:

    git clone https://github.com/rjrosati/pitherm.git
    cd pitherm
    virtualenv --python=python3 env
    source env/bin/activate
    pip install -r requirements.txt

Edit your crontab to start the scripts

    crontab -e
Mine looks like
    

Start cron on boot:

    sudo systemctl enable crond.service

# Scheduling
schedule.txt format:

    0-4 20, 4-16 80F, 16-24 20
    00-24 24
    00-24 24
    00-24 24
    00-24 24
    00-24 24
    00-24 24

on monday:

From midnight to 4 am, goal 20 degC

from 4am to 4 pm, goal 80 degF

from 4pm to midnight, goal 20 degC

every other day of week:
24 degC goal constant
