#import Adafruit_DHT
import time
import datetime
import json
import Adafruit_MCP9808.MCP9808 as MCP9808

statefile = './state.json'
logfile = './data.log'
state = {
        'DELAY': 1, #s
        'THRESHOLD': 0.5, # degC
        'HEAT_MODE': False,
        'COOL_MODE': True,
        'AC_ON': False,
        'HEAT_ON': False,
        'TEMP': float('nan'),
        'TARGET_TEMP': float('nan'),
        'CURR_PROG': '',
        'LOGGING': True,
}

def write_statefile(statefile,state):
    with open(statefile,'w') as f:
        f.write(json.dumps(state))
def read_statefile(statefile):
    with open(statefile,'r') as f:
        return json.loads(''.join(f.readlines()))

def F_to_C(t):
    return (float(t)-32)*5/9

def get_desired_temp(now):
    global state
    with open('schedule.txt','r') as f:
        lines = f.readlines()
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
            state['CURR_PROG'] = prog
            return temp
    raise Exception("Schedule file invalid, some times are unscheduled!")
def measure():
    return sensor.readTempC()
def log_data(temp,now):
    global state
    if state['LOGGING']:
        with open(logfile,'a') as f:
            data = (now.isoformat(), temp, state['AC_ON'], state['HEAT_ON'])
            datafmt = "{0} {1} {2} {3}\n"
            f.write(datafmt.format(*data))


write_statefile(statefile,state)
sensor = MCP9808.MCP9808()
sensor.begin()
while True:
    utc = datetime.datetime.utcnow()
    local = datetime.datetime.now()
    state = read_statefile(statefile)
    state['TARGET_TEMP'] = get_desired_temp(local)
    print('goal temp: ',state['TARGET_TEMP'])
    state['TEMP'] = measure()
    print('measured temp: ',state['TEMP'])
    temp = state['TEMP']
    desired_temp = state['TARGET_TEMP']
    if (temp < desired_temp - state['THRESHOLD']):
        state['AC_ON'] = False
        state['HEAT_ON'] = True
    if (temp > desired_temp + state['THRESHOLD']):
        state['AC_ON'] = True
        state['HEAT_ON'] = False
    if state['COOL_MODE']:
        if state['AC_ON']:
            print("turn on AC")
        else:
            print("turn off AC")
    if state['HEAT_MODE']:
        if state['HEAT_ON']:
            print("turn on heat")
        else:
            print("turn off heat")
    log_data(temp,utc)
    write_statefile(statefile,state)
    time.sleep(state['DELAY'])

