from flask import Flask, render_template,redirect
import json
app = Flask(__name__)
statefile = './state.json'

def write_statefile(statefile,state):
    with open(statefile,'w') as f:
        f.write(json.dumps(state))
def read_statefile(statefile):
    with open(statefile,'r') as f:
        return json.loads(''.join(f.readlines()))

@app.route('/')
def index():
    global statefile
    template_data = read_statefile(statefile)
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
    state = read_statefile(statefile)
    app.run(debug=True,host='127.0.0.1')
