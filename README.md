This is an rpi thermostat code.

Ideally, this will be simple and stupid.

I've implemented a really dumb Flask web controlling interface. This should be prettified and made mobile friendly.
As of yet there's no code for:
* actually flipping the relays
* talking to the temperature sensor
* allowing web edits of the schedule file
* logging data
* plotting data.

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