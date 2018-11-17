import time
import datetime
import json

statefile = './state.json'
logfile = './data.log'
AC_PIN = 17
HEAT_PIN = 27
state = {
        'DELAY': 20, #s
        'THRESHOLD': 0.5, # degC
        'HEAT_MODE': True,
        'COOL_MODE': False,
        'AC_ON': False,
        'HEAT_ON': False,
        'TEMP': float('nan'),
        'TARGET_TEMP': float('nan'),
        'CURR_PROG': '',
        'LOGGING': True,
        'SCHED':'sched_heat.txt',
}
TEMP_HEAT_MAX = 25 # 77 F
TEMP_COOL_MIN = 18 # 64.4F
def write_statefile(statefile,state):
    with open(statefile,'w') as f:
        f.write(json.dumps(state))
def read_statefile(statefile):
    with open(statefile,'r') as f:
        return json.loads(''.join(f.readlines()))

def F_to_C(t):
    return (float(t)-32)*5/9

def temp_from_sched(lines,now,writing=True):
    global state
    wd = now.weekday()
    sched = lines[wd]
    programs = [x.strip() for x in sched.split(',')]
    for prog in programs:
        times,temp = prog.split(' ')
        if temp.endswith('F'):
            temp = F_to_C(temp[:-1])
        else:
            temp = float(temp)
        if state['HEAT_MODE'] and temp > TEMP_HEAT_MAX:
            raise Exception("Scheduled a temperature above maximum heat limit of {} degC".format(TEMP_HEAT_MAX))
        elif state['COOL_MODE'] and temp < TEMP_COOL_MIN:
            raise Exception("Scheduled a temperature below minimum cool limit of {} degC".format(TEMP_COOL_MIN))
        earlyt, latet = map(int,times.split('-'))
        if earlyt <= now.hour < latet:
            if writing:
                state['CURR_PROG'] = prog
            return temp
    raise Exception("Some times are unscheduled!")

def get_desired_temp(now):
    global state
    with open(state['SCHED'],'r') as f:
        lines = f.readlines()
    return temp_from_sched(lines,now)
def check_schedule(text):
    lines = text.split('\n')
    now = datetime.datetime.now()
    now_1wk = now + datetime.timedelta(days=7)
    onehr = datetime.timedelta(hours=1)
    while now < now_1wk:
        try:
            temp_from_sched(lines,now,False)
        except Exception as e:
            return False,"Schedule file not updated. "+str(e)
        now += onehr
    return True,'Schedule file successfully updated!'
def measure():
    return sensor.readTempC()
def log_data(temp,now):
    global state
    if state['LOGGING']:
        with open(logfile,'a') as f:
            data = (now.isoformat(), temp, state['AC_ON'], state['HEAT_ON'],state['TARGET_TEMP'],state['THRESHOLD'])
            datafmt = "{0} {1} {2} {3} {4} {5}\n"
            f.write(datafmt.format(*data))

def AC_ON():
    print("AC ON")
    GPIO.output(AC_PIN,1)
def AC_OFF():
    print("AC OFF")
    GPIO.output(AC_PIN,0)
def HEAT_ON():
    print("HEAT ON")
    GPIO.output(HEAT_PIN,1)
def HEAT_OFF():
    print("HEAT OFF")
    GPIO.output(HEAT_PIN,0)

if __name__=='__main__':
    import Adafruit_MCP9808.MCP9808 as MCP9808
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([AC_PIN,HEAT_PIN],GPIO.OUT)

    write_statefile(statefile,state)
    sensor = MCP9808.MCP9808()
    sensor.begin()
    while True:
        utc = datetime.datetime.utcnow()
        local = datetime.datetime.now()
        state = read_statefile(statefile)
        state['TARGET_TEMP'] = get_desired_temp(local)
        print('goal temp: ',state['TARGET_TEMP'])
        try:
            state['TEMP'] = measure()
        except OSError:
            state['TEMP'] = float('nan')
            print('measurement error')
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
            state['SCHED'] = 'sched_cool.txt'
            if state['AC_ON']:
                AC_ON()
            else:
                AC_OFF()
        else:
            AC_OFF()
        if state['HEAT_MODE']:
            state['SCHED'] = 'sched_heat.txt'
            if state['HEAT_ON']:
                HEAT_ON()
            else:
                HEAT_OFF()
        else:
            HEAT_OFF()
        log_data(temp,utc)
        write_statefile(statefile,state)
        time.sleep(state['DELAY'])

