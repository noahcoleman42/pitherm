from flask import Flask, render_template,redirect
import json
import time
app = Flask(__name__)
statefile = './state.json'
plotfile = './plot.html'

def write_statefile(statefile,state):
    with open(statefile,'w') as f:
        f.write(json.dumps(state))
def read_statefile(statefile):
    with open(statefile,'r') as f:
        return json.loads(''.join(f.readlines()))

@app.route('/')
def index():
    global statefile,lastupdate,updaterate,plotdata
    template_data = read_statefile(statefile)
    if os.path.exists(plotfile):
        with open(plotfile,'r') as f:
            plotdata = f.readall()
        template_data['plot'] = plotdata
    else:
        template_data['plot'] = " Waiting for plot data... Did you start the plotting script? Refresh in a few minutes!"
    return render_template('index.html',**template_data)

@app.route('/<action>/<switch>')
def button_press(action,switch):
    global state
    global statefile
    if action=='cool':
        if switch=='on':
            state['COOL_MODE'] = True
            write_statefile(statefile,state)
        elif switch=='off':
            state['COOL_MODE'] = False
            write_statefile(statefile,state)
    elif action=='heat':
        if switch=='on':
            state['HEAT_MODE'] = True
            write_statefile(statefile,state)
        elif switch=='off':
            state['HEAT_MODE'] = False
            write_statefile(statefile,state)
    else:
        print('unrecognized url!')
    state = read_statefile(statefile)
    return redirect('/')


if __name__ == '__main__':
    import configparser
    conf = configparser.ConfigParser()
    conf.read(creds)
    up = conf['creds']
    plotly.tools.set_credentials_file(username=up['user'], api_key=up['key'])
    state = read_statefile(statefile)
    app.run(debug=True,host='0.0.0.0')
