This is an rpi thermostat code.

Ideally, this will be simple and stupid.

I've implemented a really dumb Flask web controlling interface. This should be prettified and made mobile friendly.
As of yet there's no code for:
* actually flipping the relays
* allowing web edits of the schedule file
* logging data
* plotting data.

# Installation
First, you'll need to connect your Pi to your MCP9808 and relays. My circuit is
[[diagram]]

Then you can install the software:

    sudo apt update
    sudo apt upgrade
    sudo apt install git virtualenv crontab ntp

Let those install, then run `raspi-config` and do the following:
* set your time zone
* enable the I2C interface

Reboot, then you should be able to install `pitherm`:

    git clone https://github.com/rjrosati/pitherm.git
    cd pitherm
    virtualenv --python=python3 env
    source env/bin/activate
    pip install -r requirements.txt

Edit your crontab to start the temperature checking script and the flask webserver.
TODO: pass data between them in `multiprocessing.Queue`

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
