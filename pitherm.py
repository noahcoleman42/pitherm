#import Adafruit_DHT
import time
import datetime

DELAY = 1 #s
THRESHOLD = 0.5 # degC
HEAT_MODE = False
COOL_MODE = True
AC_ON = False
HEAT_ON = False

def F_to_C(t):
    return (float(t)-32)*5/9

def get_desired_temp():
    with open('schedule.txt','r') as f:
        lines = f.readlines()
    now = datetime.datetime.now()
    wd = now.weekday()
    sched = lines[wd]
    programs = [x.strip() for x in sched.split(',')]
    for prog in programs:
        times,temp = prog.split(' ')
        if temp.endswith('F'):
            temp = F_to_C(temp)
        else:
            temp = float(temp)
        earlyt, latet = map(int,times.split('-'))
        if earlyt < now.hour < latet:
            return temp
    raise Exception("Schedule file invalid, some times are unscheduled!")
        
def measure():
    return float(input('enter measured temp: '))

while True:
    desired_temp = get_desired_temp()
    print('goal temp: ',desired_temp)
    temp = measure()
    if (temp < desired_temp - THRESHOLD):
        AC_ON = False
        HEAT_ON = True
    if (temp > desired_temp + THRESHOLD):
        AC_ON = True
        HEAT_ON = False
    if COOL_MODE:
        if AC_ON:
            print("turn on AC")
        else:
            print("turn off AC")
    if HEAT_MODE:
        if HEAT_ON:
            print("turn on heat")
        else:
            print("turn off heat")

    time.sleep(DELAY)

