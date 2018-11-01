from flask import Flask, render_template,redirect,request
import json
import time
import os.path
from pitherm import check_schedule
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
            plotdata = f.read()
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
    return redirect('../..')

@app.route('/edit')
def get_schedule():
    global statefile
    state = read_statefile(statefile)
    with open(state['SCHED'],'r') as f:
        text = f.read()
    template_data = dict()
    template_data['text'] = text
    template_data['err_msg'] = ''
    return render_template('edit.html',**template_data)
@app.route('/edit',methods=['POST'])
def save_schedule():
    global statefile
    sched_text = request.form['text']
    template_data=dict()
    success, err_msg = check_schedule(sched_text)
    if success:
        lines = sched_text.split('\n')
        lines = lines[:8]
        with open(state['SCHED'],'w') as f:
            f.write('\n'.join(lines))
        template_data['text'] = sched_text
        template_data['err_msg'] = err_msg
        return render_template('edit.html',**template_data)
    else:
        template_data['text'] = sched_text
        template_data['err_msg'] = err_msg
        return render_template('edit.html',**template_data)

if __name__ == '__main__':
    state = read_statefile(statefile)
    app.run(debug=True,host='0.0.0.0')
