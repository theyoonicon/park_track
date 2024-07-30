
import matplotlib.pyplot as plt
import matplotlib
plt.rc('font', family='Malgun Gothic')
matplotlib.use('Agg')
import matplotlib.dates as mdates
from scipy.interpolate import make_interp_spline
import numpy as np

import io
import base64

import pandas as pd

import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio


def create_interactive_graph(df):
    """ Create an interactive graph from the DataFrame using Plotly """
    if df.empty:
        return None

    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    events = {"좋아요": 1, "보통이에요": 2, "나빠요": 3}
    df['event_num'] = df['event'].map(events)

    trace_symptoms = go.Scatter(
        x=df[df['type'] == 'symptom']['time'],
        y=df[df['type'] == 'symptom']['event_num'],
        mode='lines+markers',
        name='Symptoms',
        marker=dict(color='blue')
    )

    trace_medications = go.Scatter(
        x=df[df['type'] == 'medication']['time'],
        y=df[df['type'] == 'medication']['event_num'],
        mode='markers',
        name='Medications',
        marker=dict(color='red', symbol='triangle-up')
    )

    layout = go.Layout(
        title='Symptom and Medication Over Time',
        xaxis=dict(title='Time'),
        yaxis=dict(
            title='Event',
            tickvals=[1, 2, 3],
            ticktext=["좋아요", "보통이에요", "나빠요"]
        ),
        height=600,
        width=1000
    )

    fig = go.Figure(data=[trace_symptoms, trace_medications], layout=layout)

    graph_html = pio.to_html(fig, full_html=False)
    return graph_html



def create_graph(df, date_filter):
    """ Create a graph from the DataFrame and return as base64 string """
    plt.figure(figsize=(10, 5))
    
    if df.empty:
        plt.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', fontsize=12)
        plt.axis('off')
    else:
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        events = {"좋아요": 3, "보통이에요": 2, "나빠요": 1}
        df['event_num'] = df['event'].map(events)
        
        # Separate symptom and medication events
        df_symptom = df[df['type'] == 'symptom']
        df_medication = df[df['type'] == 'medication']
        
        # Remove NaNs and infinite values from symptom events
        df_symptom = df_symptom.dropna(subset=['time', 'event_num'])
        df_symptom = df_symptom[np.isfinite(df_symptom['event_num'])]
        
        # 자정에서 다음날 자정으로 x축 고정
        start_time = pd.to_datetime(date_filter)
        end_time = start_time + pd.DateOffset(days=1)
        plt.xlim([start_time, end_time])

        ### 직선
        # plt.plot(df['time'], df['event_num'], marker='o', linestyle='-', color='b', label='Event')
        
        ### 곡선으로 연결
        # 곡선으로 연결 (symptom events)
        x = mdates.date2num(df_symptom['time'])
        y = df_symptom['event_num']
        
        # Check if there are enough points to create a spline
        if len(x) > 3 and len(y) > 3:
            # Create spline
            x_new = np.linspace(x.min(), x.max(), 300) 
            spl = make_interp_spline(x, y, k=3)
            y_smooth = spl(x_new)
            
            plt.plot(mdates.num2date(x_new), y_smooth, marker='o', linestyle='-', color='b', label='Symptom Event')
        else:
            plt.plot(df_symptom['time'], df_symptom['event_num'], marker='o', linestyle='-', color='b', label='Symptom Event')
        
        
        # Plot medication events
        for i, row in df_medication.iterrows():
            plt.annotate('약 섭취', xy=(row['time'], 2),
                         xytext=(row['time'], 2.5),
                         arrowprops=dict(facecolor='red', shrink=0.05))

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.xticks(rotation=45)
        
        plt.yticks([1, 2, 3], ["나빠요", "보통이에요", "좋아요"])
        plt.xlabel('Time')
        plt.ylabel('Event')
        plt.title('Symptom and Medication Over Time')
        plt.legend()
        plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return 'data:image/png;base64,{}'.format(graph_url)

# pandas
def query_to_dataframe(query):
    """ Convert query result to Pandas DataFrame """
    data = []
    for symptom in query:
        data.append({
            'id': symptom.id,
            'username': symptom.username,
            'time': symptom.time,
            'event': symptom.event,
            'type': symptom.type
        })
    return pd.DataFrame(data)
