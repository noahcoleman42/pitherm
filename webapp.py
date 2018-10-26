from flask import Flask, render_template,redirect
import json
import numpy as np
from plotly.offline import download_plotlyjs,plot,iplot
import plotly.graph_objs as go
from datetime import datetime
import dateutil.parser
import pytz
import time
app = Flask(__name__)
statefile = './state.json'
datafile = './data.log'

def write_statefile(statefile,state):
    with open(statefile,'w') as f:
        f.write(json.dumps(state))
def read_statefile(statefile):
    with open(statefile,'r') as f:
        return json.loads(''.join(f.readlines()))
def update_plot():
    t = time.time()
    tmp = np.loadtxt(datafile,usecols=1)
    sched = np.loadtxt(datafile,usecols=4)
    thresh = np.loadtxt(datafile,usecols=5)
    dates = []
    with open(datafile,'r') as f:
        for line in f:
            #naive = datetime.fromisoformat(line.split()[0])
            naive = dateutil.parser.parse(line.split()[0])
            tz_aware = naive.replace(tzinfo=pytz.utc)
            tz_aware = tz_aware.astimezone(pytz.timezone('America/Chicago'))
            naive = tz_aware.replace(tzinfo=None) #plot.ly won't display tz-aware datetime objects properly
            # https://github.com/plotly/plotly.py/issues/209
            dates.append(naive)
    data = [
            go.Scatter(x=dates, y=tmp,name='temp'),
            go.Scatter(x=dates, y=sched,name='sched',legendgroup='sched'),
            go.Scatter(x=dates, y=sched+thresh, fill=None, mode=None, line={'color':'yellow'},
                       showlegend=False, legendgroup='sched',hoverinfo='skip',opacity=0.1),
            go.Scatter(x=dates, y=sched-thresh, fill='tonexty', mode=None, line={'color':'yellow'},
                       showlegend=False, legendgroup='sched',hoverinfo='skip',opacity=0.1),
           ]
    layout = dict(
        title='Gelbes Haus Thermostat',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=10,
                         label='10h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=1,
                         label='1d',
                         step='day',
                         stepmode='backward'),
                    dict(count=7,
                         label='7d',
                         step='day',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible = True
            ),
            type='date'
        )
    )

    fig = dict(data=data, layout=layout)
    div = plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
    print("took",time.time()-t,'s')
    return div


lastupdate = 0
updaterate = 20
plotdata = ''
@app.route('/')
def index():
    global statefile,lastupdate,updaterate,plotdata
    template_data = read_statefile(statefile)
    if time.time() - lastupdate > updaterate:
        lastupdate=time.time()
        plotdata = update_plot()
    template_data['plot'] = plotdata
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
    app.run(debug=True,host='0.0.0.0')
