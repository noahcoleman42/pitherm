from plotly.offline import plot,download_plotlyjs
import plotly.graph_objs as go
from datetime import datetime
import dateutil.parser
import pytz
import time
import numpy as np

datafile = './data.log'
creds = './creds.ini'
plotfile = './plot.html'
updaterate = 30*60

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
            go.Scatter(x=dates, y=tmp,name='temp',connectgaps=False),
            go.Scatter(x=dates, y=sched,name='sched',legendgroup='sched',connectgaps=False),
            go.Scatter(x=dates, y=sched+thresh, fill=None, mode=None, line={'color':'yellow'},
                       showlegend=False, legendgroup='sched',hoverinfo='skip',opacity=0.1,connectgaps=False),
            go.Scatter(x=dates, y=sched-thresh, fill='tonexty', mode=None, line={'color':'yellow'},
                       showlegend=False, legendgroup='sched',hoverinfo='skip',opacity=0.1,connectgaps=False),
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
    plotdata = plot(fig,output_type='div',include_plotlyjs=True)
    print("took",time.time()-t,'s')
    with open(plotfile,'w') as f:
        f.write(plotdata)

if __name__ == '__main__':
    while True:
        try:
            update_plot()
        except ValueError:
            sleep(1)
            pass
        time.sleep(updaterate)
